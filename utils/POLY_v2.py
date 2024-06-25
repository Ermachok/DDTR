import bisect
import json
import math
import os.path
import statistics
from pathlib import Path

import matplotlib.pyplot as plt
from utils.gains import GainsEquator, Gains_T15_35, Gains_T15_34
from utils.caen_handler import handle_all_caens_multiproces


class Polychromator:
    def __init__(self, poly_name: int | str, fiber_number: int, z_cm: float, caen_time: list, caen_data: list,
                 config_connection=None, gains: GainsEquator | Gains_T15_34 | Gains_T15_35 = None,
                 absolut_calib: Path = None, spectral_calib: Path = None, f_expect_path: Path = None):

        """
        :param poly_name: номер полихроматора в стойке!
        :param fiber_number: номер волокна, 1 - вверх
        :param caen_time: приведенные к по максимуму времена
        :param caen_data: данные с каена, 5 каналов
        :param config_connection: конфиг
        :param absolut_calib:
        """

        self.poly_name = poly_name
        self.fiber_number = fiber_number
        self.z_cm = z_cm

        self.signals = caen_data
        self.signals_time = caen_time
        self.ch_number = len(self.signals)
        self.gain = gains

        self.signals_integrals = None
        self.signals_noise_integrals = None

        self.f_expected_path = f_expect_path
        self.expected_data = None
        self.config = config_connection

        self.spectral_calibration = None
        self.absolut_calibration = None

        self.load_spectral_calibration(spectral_calib_path=spectral_calib)
        self.load_absolut_calibration(absolut_calib_path=absolut_calib)

        self.integralsPhe = []
        self.noisePhe = []
        self.average_parasite = None

        self.temperatures = []
        self.density = []

        self.errors_T = []
        self.errors_n = []

    def load_spectral_calibration(self, spectral_calib_path):
        try:
            with open(spectral_calib_path, 'r') as spec_file:
                spectral_data = json.load(spec_file)
            for key in spectral_data.keys():
                if str.lower(self.poly_name).startswith(str.lower(key)):
                    self.spectral_calibration = spectral_data[key]
            if not self.spectral_calibration:
                print(f'{self.poly_name} NO SPECTRAL CALIBRATION DATA')

        except Exception as e:
            print(f'{self.poly_name} NO SPECTRAL CALIBRATION DATA, {e}')
            pass

    def load_absolut_calibration(self, absolut_calib_path):
        try:
            with open(absolut_calib_path, 'r') as absolut_file:
                self.absolut_calibration = json.load(absolut_file)[self.poly_name]
                pass
        except Exception as e:
            print(f'\n{self.poly_name} NO ABSOLUTE CALIBRATION DATA, {e}')
            pass

    def get_signal_integrals(self, shots_before_plasma: int = 4, shots_after: int = 17,
                             t_step: float = 0.325) -> tuple[list, list]:
        """
        RETURNS PHE
        :param shots_before_plasma:
        :param shots_after:
        :param number_of_ch:
        :param t_step:
        :return:
        """

        all_const = self.gain.resulting_multiplier
        noise_len = 400

        all_shots_signal = []
        all_shots_noise = []
        for shot in range(1, shots_before_plasma + shots_after):
            all_ch_signal = []
            all_ch_noise = []
            for poly_ch in range(self.ch_number):
                signal_ind = [bisect.bisect_left(self.signals_time[shot], self.config[poly_ch]['sig_LeftBord']),
                              bisect.bisect_right(self.signals_time[shot], self.config[poly_ch]['sig_RightBord'])]

                signal_lvl = statistics.median(self.signals[poly_ch][shot][:noise_len])
                lvl_integral = signal_lvl * (self.config[poly_ch]['sig_RightBord'] - self.config[poly_ch]['sig_LeftBord'])
                signal_integral = sum(self.signals[poly_ch][shot][signal_ind[0]:signal_ind[1]]) * t_step - lvl_integral

                all_ch_signal.append(signal_integral * all_const)

                all_ch_noise.append((statistics.stdev(self.signals[poly_ch][shot][:200])) * all_const * t_step *
                                    (signal_ind[1] - signal_ind[0]))

            all_shots_signal.append(all_ch_signal)
            all_shots_noise.append(all_ch_noise)

        self.integralsPhe = all_shots_signal.copy()
        self.noisePhe = all_shots_noise.copy()

        return all_shots_signal, all_shots_noise

    def get_temperatures(self, print_flag=False):
        """
        GIVES TEMPERATURE LIST
        :return:
        """
        fe_data = self.get_expected_fe()
        self.signals_integrals, self.signals_noise_integrals = self.get_signal_integrals()
        ch_nums = self.ch_number
        results = []
        for shot, noise in zip(self.signals_integrals, self.signals_noise_integrals):
            ans = []
            for index, (T_e, f_e) in enumerate(fe_data.items()):
                khi = 0
                if index >= 2:

                    sum_1 = 0
                    for ch in range(ch_nums):
                        sum_1 += shot[ch] * (f_e[ch] * self.spectral_calibration[ch]) / noise[ch] ** 2

                    sum_2 = 0
                    for ch in range(ch_nums):
                        sum_2 += (f_e[ch] * self.spectral_calibration[ch]) ** 2 / noise[ch] ** 2

                    for ch in range(ch_nums):
                        khi += (shot[ch] - sum_1 * (f_e[ch] * self.spectral_calibration[ch]) / sum_2) ** 2 / noise[
                            ch] ** 2
                    ans.append({T_e: khi})

            results.append(ans)

        for shot in results:
            sort = sorted(shot, key=lambda x: list(x.values())[0])
            for T in sort[0].keys():
                self.temperatures.append(T)
                if print_flag:
                    print(round(float(T), 3), end=', ')
        if print_flag:
            print()

    def get_density(self, print_flag=False):

        laser_energy = 1.5
        elector_radius = 6.652E-29

        fe_data = self.get_expected_fe()

        if not self.temperatures:
            self.get_temperatures()

        for shot, noise, T_e in zip(self.signals_integrals, self.signals_noise_integrals, self.temperatures):
            sum_numerator = 0
            sum_divider = 0
            for ch in range(self.ch_number):
                sum_numerator += shot[ch] * (fe_data[T_e][ch] * self.spectral_calibration[ch]) / noise[ch] ** 2
                sum_divider += (fe_data[T_e][ch] * self.spectral_calibration[ch]) ** 2 / noise[ch] ** 2

            self.density.append(str(sum_numerator / (sum_divider * laser_energy *
                                                     self.absolut_calibration * elector_radius)))
            if print_flag:
                print('%.2e' % (sum_numerator / (sum_divider * laser_energy *
                                                 self.absolut_calibration * elector_radius)), end=' ')
        if print_flag:
            print()

    def get_errors(self, laser_energy: float = 1.5):
        ch_nums = self.ch_number
        electron_radius = 6.6e-29

        fe_data = self.get_expected_fe()
        for shot_noise, T_e in zip(self.noisePhe, self.temperatures):
            try:
                shot_num = self.noisePhe.index(shot_noise)
                T_e_ind = fe_data['Te_grid'].index(float(T_e))
                T_e_next = str(fe_data['Te_grid'][T_e_ind + 1])

                sum_fe_to_noise = 0
                sum_derivative_fe_to_noise = 0
                sum_fe_derivative_fe_to_noise = 0
                T_e_step = float(T_e_next) - float(T_e)
                for ch in range(ch_nums):
                    derivative_fe = (fe_data[T_e][ch] - fe_data[T_e_next][ch]) / T_e_step

                    sum_fe_to_noise += (fe_data[T_e][ch] / shot_noise[ch]) ** 2
                    sum_derivative_fe_to_noise += (derivative_fe / shot_noise[ch]) ** 2
                    sum_fe_derivative_fe_to_noise += (derivative_fe * fe_data[T_e][ch] / shot_noise[ch] ** 2) ** 2

                M_errT = sum_fe_to_noise / (
                        sum_fe_to_noise * sum_derivative_fe_to_noise - sum_fe_derivative_fe_to_noise)

                M_errn = sum_derivative_fe_to_noise / (
                        sum_fe_to_noise * sum_derivative_fe_to_noise - sum_fe_derivative_fe_to_noise)

                self.errors_T.append(str(math.sqrt(M_errT / electron_radius ** 2 /
                                                   (self.absolut_calibration * float(
                                                      self.density[shot_num]) * laser_energy) ** 2)))

                self.errors_n.append(str(math.sqrt(M_errn / electron_radius ** 2 /
                                                   (self.absolut_calibration * laser_energy) ** 2)))
            except (IndexError, ZeroDivisionError, ValueError):
                self.errors_T.append(0)
                self.errors_n.append(0)

    @staticmethod
    def rude_pest_check(signals_before_plasma, signal_lvl,
                        start_ind: int = 500, end_ind: int = 700, t_step: float = 0.325):
        """
        :param signals_before_plasma: количество выстрелов перед плазмой
        :param start_ind: номер ячейки из оцифровщика, с которой начинается считаться интеграл
        :param end_ind: конец окна интегрирования - старт и конец выбраны с запасом из знания о том, где расположен паразит
        :param t_step: шаг оцифровщика
        :return: есть паразит или нет
        """
        pestSum = 0
        for shot in signals_before_plasma:
            pestSum += sum(shot[start_ind:end_ind])
        pest = pestSum / len(signals_before_plasma) * t_step - signal_lvl * (end_ind - start_ind) * t_step
        if pest > 100:
            # print('Average summ in pest area: {pest} mV * ns\n'
            # 'There is a chance of a parasite existing'.format(pest=pest))
            return pest
        return False

    def signal_approx(self):
        pass

    def get_expected_fe(self):
        path: str = self.f_expected_path
        with open(path, 'r') as f_file:
            fe_data = json.load(f_file)
        return fe_data

    def get_expected_phe(self):
        f_e = self.get_expected_fe()
        from_shot = 5
        to_shot = 20

        electron_radius = 6.6E-29
        laser_energy = 1.5

        for shot, T_e, n_e in zip(self.integralsPhe[from_shot:to_shot],
                                  self.temperatures[from_shot:to_shot],
                                  self.density[from_shot:to_shot]):
            print('shot_number ', self.integralsPhe.index(shot), end='  ')
            print(T_e, n_e,
                  'got ', shot[0], 'expected', self.absolut_calibration * f_e[T_e][0] * electron_radius * laser_energy * float(n_e),
                  'got', shot[1], 'expected', self.absolut_calibration * f_e[T_e][1] * electron_radius * laser_energy * float(n_e))

    def plot_expected(self):
        pass

    def plot_raw_signals(self, from_shot: int = 10, to_shot: int | str = 20):
        fig, ax = plt.subplots(nrows=len(self.signals), ncols=1, figsize=(13, 8))

        if int == type(to_shot):
            pass
        elif str.lower(to_shot) == 'all':
            to_shot = len(self.signals[0])

        for ch in range(len(self.signals)):
            for shot in range(from_shot, to_shot):
                time, signal = self.get_raw_data(shot_num=shot, ch_num=ch)
                ax[ch].plot(time, signal, label='shot %d' % shot)
                ax[ch].set_xlim([0, 80])
        ax[0].legend(ncol=3)
        plt.subplots_adjust(left=0.05, right=0.95, top=0.96, bottom=0.07)
        ax[0].set_title(f"{self.poly_name}")
        plt.show()

    def get_raw_data(self, shot_num: int = None, ch_num: int = None):
        if ch_num is None and shot_num is None:
            return self.signals_time, self.signals
        return self.signals_time[shot_num], self.signals[ch_num][shot_num]


    def write_raw_signals(self, path: Path):

        path_entry = os.path.join(path, self.poly_name)
        for ch in range(self.ch_number):
            path = path_entry + f'_{ch+1}channel.csv'
            with open(path, 'w') as w_file:
                for count in range(1024):
                    string = f'{count*0.325}, '
                    for shot in self.signals[ch]:
                        string +=f'{str(shot[count])}, '
                    w_file.write(string + '\n')


def built_fibers(discharge_num: str, config: dict, calibration_flag: bool = False) -> (list, list[Polychromator]):

    with open(config['poly_fiber_caen_connection']) as file:
        config_connection = json.load(file)

    msg_list = [0, 1, 2, 3]

    if calibration_flag:
        all_caens = handle_all_caens_multiproces(discharge_num=discharge_num, path=config['path_calib_data'],
                                                 msg_list=msg_list, processed_shots='all')
    else:
        all_caens = handle_all_caens_multiproces(discharge_num=discharge_num, path=config['path_experimental_data'],
                                                 msg_list=msg_list, processed_shots=30)

    combiscope_times = all_caens[0]['combiscope_times']
    handmade_poly_data = all_caens[0]['caen_channels'][2:6]
    handmade_poly_data.insert(0, all_caens[1]['caen_channels'][6])

    equatorGain = GainsEquator()
    t15_34_Gain = Gains_T15_34()
    t15_35_Gain = Gains_T15_35()

    poly_handmade = Polychromator(poly_name="Handmade_G10", fiber_number=1, z_cm=-35.7,
                                  config_connection=config_connection['equator_caens'][0]['channels'][2:6],
                                  gains=equatorGain, f_expect_path=None,
                                  spectral_calib=config['path_spectral_calibration'],
                                  caen_time=all_caens[0]['shots_time'], caen_data=handmade_poly_data)

    poly_042 = Polychromator(poly_name="eqTS_42_G10", fiber_number=2, z_cm=-37.1,
                             config_connection=config_connection['equator_caens'][2]['channels'][1:5],
                             gains=equatorGain, f_expect_path=config['path_eq_f_exp'],
                             spectral_calib=config['path_spectral_calibration'],
                             absolut_calib=config['path_absolute_calibration'],
                             caen_time=all_caens[2]['shots_time'], caen_data=all_caens[2]['caen_channels'][1:5])

    poly_047 = Polychromator(poly_name="eqTS_47_G10", fiber_number=3, z_cm=-38.6,
                             config_connection=config_connection['equator_caens'][2]['channels'][6:10],
                             gains=equatorGain, f_expect_path=config['path_eq_f_exp'],
                             spectral_calib=config['path_spectral_calibration'],
                             absolut_calib=config['path_absolute_calibration'],
                             caen_time=all_caens[2]['shots_time'], caen_data=all_caens[2]['caen_channels'][6:10])

    poly_048 = Polychromator(poly_name="eqTS_48_G10", fiber_number=4, z_cm=-39.9,
                             config_connection=config_connection['equator_caens'][2]['channels'][11:15],
                             gains=equatorGain, f_expect_path=config['path_eq_f_exp'],
                             spectral_calib=config['path_spectral_calibration'],
                             absolut_calib=config['path_absolute_calibration'],
                             caen_time=all_caens[2]['shots_time'], caen_data=all_caens[2]['caen_channels'][11:15])

    poly_049 = Polychromator(poly_name="eqTS_49_G10", fiber_number=5, z_cm=-41,
                             config_connection=config_connection['equator_caens'][3]['channels'][1:5],
                             gains=equatorGain, f_expect_path=config['path_eq_f_exp'],
                             spectral_calib=config['path_spectral_calibration'],
                             absolut_calib=config['path_absolute_calibration'],
                             caen_time=all_caens[3]['shots_time'], caen_data=all_caens[3]['caen_channels'][1:5])

    poly_050 = Polychromator(poly_name="eqTS_50_G10", fiber_number=6, z_cm=-42.2,
                             config_connection=config_connection['equator_caens'][3]['channels'][6:10],
                             gains=equatorGain, f_expect_path=config['path_eq_f_exp'],
                             spectral_calib=config['path_spectral_calibration'],
                             absolut_calib=config['path_absolute_calibration'],
                             caen_time=all_caens[3]['shots_time'], caen_data=all_caens[3]['caen_channels'][6:10])

    poly_T15_34 = Polychromator(poly_name="T15_34_G10", fiber_number=7, z_cm=-43.25,
                                config_connection=config_connection['equator_caens'][1]['channels'][11:15],
                                gains=t15_34_Gain, f_expect_path=config['path_T15_f_exp'],
                                spectral_calib=config['path_spectral_calibration'],
                                absolut_calib=config['path_absolute_calibration'],
                                caen_time=all_caens[1]['shots_time'], caen_data=all_caens[1]['caen_channels'][11:15])

    poly_T15_35 = Polychromator(poly_name="T15_35_G10", fiber_number=8, z_cm=-44.35,
                                config_connection=config_connection['equator_caens'][3]['channels'][11:15],
                                gains=t15_35_Gain, f_expect_path=config['path_T15_f_exp'],
                                spectral_calib=config['path_spectral_calibration'],
                                absolut_calib=config['path_absolute_calibration'],
                                caen_time=all_caens[3]['shots_time'], caen_data=all_caens[3]['caen_channels'][11:15])

    poly_novosib = Polychromator(poly_name="Novosib", fiber_number=9, z_cm=-45.55,
                                 config_connection=config_connection['equator_caens'][0]['channels'][6:10],
                                 gains=equatorGain, f_expect_path=None,
                                 spectral_calib=config['path_spectral_calibration'],
                                 caen_time=all_caens[0]['shots_time'], caen_data=all_caens[0]['caen_channels'][6:10])

    del all_caens

    fibers = [poly_042, poly_047, poly_048, poly_049, poly_050, poly_T15_34, poly_T15_35]

    return combiscope_times, fibers


def calculate_Te_ne(fibers: Polychromator | list[Polychromator]):
    for fiber in fibers:
        fiber.get_temperatures(print_flag=False)
        fiber.get_density(print_flag=False)
        fiber.get_errors()