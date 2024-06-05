import json

from utils.POLY_v2 import Polychromator
from utils.caen_handler import handle_all_caens_multiproces
from utils.calibration_utils import calculate_calibration_coef
from utils.gains import GainsEquator, Gains_T15_34, Gains_T15_35

discharge_num = '00913'
spec_calib_file = 'EN_spectral_config_2024_05_14.json'
abs_calib_file = 'EN_absolut_2024'

path_ophir = r'D:\Ioffe\TS\divertor_thomson\calibration\05.2024\Ophir_data'
ophir_shot_name = '75_18.txt'

path_calib_experimental_data = r'D:\Ioffe\TS\divertor_thomson\calibration\05.2024\caen_files'

path_spectral_calibration = (fr'D:\Ioffe\TS\divertor_thomson\different_calcuations_py\DTS_main'
                             fr'\script\absolut_calibration\calibration_may2024\calibration_config'
                             fr'\{spec_calib_file}')

path_absolute_calibration = (fr'')

path_eq_f_exp = (r'D:/Ioffe/TS/divertor_thomson/different_calcuations_py/DTS_main'
                 r'/script_DTS/absolut_calibration/calibration_may2024/utils/f_expected_eq.json')

path_T15_f_exp = (r'D:/Ioffe/TS/divertor_thomson/different_calcuations_py/DTS_main'
                  r'/script_DTS/absolut_calibration/calibration_may2024/utils/f_expected_T15.json')

if __name__ == '__main__':
    with open('config_connection_05_2024') as file:
        config_connection = json.load(file)

    # all_caens = handle_all_caens(discharge_num=discharge_num, path=path_experimental_data, processed_shots=20) -
    # previous version

    msg_list = [0, 1, 2, 3]
    all_caens = handle_all_caens_multiproces(discharge_num=discharge_num, path=path_calib_experimental_data,
                                             msg_list=msg_list, processed_shots='all')

    handmade_poly_data = all_caens[0]['caen_channels'][2:6]
    handmade_poly_data.insert(0, all_caens[1]['caen_channels'][6])

    equatorGain = GainsEquator()
    t15_34_Gain = Gains_T15_34()
    t15_35_Gain = Gains_T15_35()

    poly_handmade = Polychromator(poly_name="Handmade_G10", fiber_number=1, z_cm=-35.7,
                                  config_connection=config_connection['equator_caens'][0]['channels'][2:6],
                                  gains=equatorGain, f_expect_path=None,
                                  spectral_calib=path_spectral_calibration,
                                  caen_time=all_caens[0]['shots_time'], caen_data=handmade_poly_data)

    poly_042 = Polychromator(poly_name="eqTS_42_G10", fiber_number=2, z_cm=-37.1,
                             config_connection=config_connection['equator_caens'][2]['channels'][1:5],
                             gains=equatorGain, f_expect_path=path_eq_f_exp,
                             spectral_calib=path_spectral_calibration,
                             caen_time=all_caens[2]['shots_time'], caen_data=all_caens[2]['caen_channels'][1:5])

    poly_047 = Polychromator(poly_name="eqTS_47_G10", fiber_number=3, z_cm=-38.6,
                             config_connection=config_connection['equator_caens'][2]['channels'][6:10],
                             gains=equatorGain,
                             spectral_calib=path_spectral_calibration, f_expect_path=path_eq_f_exp,
                             caen_time=all_caens[2]['shots_time'], caen_data=all_caens[2]['caen_channels'][6:10])

    poly_048 = Polychromator(poly_name="eqTS_48_G10", fiber_number=4, z_cm=-39.9,
                             config_connection=config_connection['equator_caens'][2]['channels'][11:15],
                             gains=equatorGain,
                             spectral_calib=path_spectral_calibration, f_expect_path=path_eq_f_exp,
                             caen_time=all_caens[2]['shots_time'], caen_data=all_caens[2]['caen_channels'][11:15])

    poly_049 = Polychromator(poly_name="eqTS_49_G10", fiber_number=5, z_cm=-41,
                             config_connection=config_connection['equator_caens'][3]['channels'][1:5],
                             gains=equatorGain,
                             spectral_calib=path_spectral_calibration, f_expect_path=path_eq_f_exp,
                             caen_time=all_caens[3]['shots_time'], caen_data=all_caens[3]['caen_channels'][1:5])

    poly_050 = Polychromator(poly_name="eqTS_50_G10", fiber_number=6, z_cm=-42.2,
                             config_connection=config_connection['equator_caens'][3]['channels'][6:10],
                             gains=equatorGain,
                             spectral_calib=path_spectral_calibration, f_expect_path=path_eq_f_exp,
                             caen_time=all_caens[3]['shots_time'], caen_data=all_caens[3]['caen_channels'][6:10])

    poly_T15_34 = Polychromator(poly_name="T15_34_G10", fiber_number=7, z_cm=-43.25,
                                config_connection=config_connection['equator_caens'][1]['channels'][11:15],
                                gains=t15_34_Gain,
                                spectral_calib=path_spectral_calibration, f_expect_path=path_T15_f_exp,
                                caen_time=all_caens[1]['shots_time'], caen_data=all_caens[1]['caen_channels'][11:15])

    poly_T15_35 = Polychromator(poly_name="T15_35_G10", fiber_number=8, z_cm=-44.35,
                                config_connection=config_connection['equator_caens'][3]['channels'][11:15],
                                gains=t15_35_Gain,
                                spectral_calib=path_spectral_calibration, f_expect_path=path_T15_f_exp,
                                caen_time=all_caens[3]['shots_time'], caen_data=all_caens[3]['caen_channels'][11:15])

    poly_novosib = Polychromator(poly_name="Novosib", fiber_number=9, z_cm=-45.55,
                                 config_connection=config_connection['equator_caens'][0]['channels'][6:10],
                                 gains=equatorGain,
                                 spectral_calib=path_spectral_calibration, f_expect_path=None,
                                 caen_time=all_caens[0]['shots_time'], caen_data=all_caens[0]['caen_channels'][6:10])

    del all_caens

    fibers = [poly_handmade, poly_042, poly_047, poly_048, poly_049, poly_050, poly_T15_34, poly_T15_35, poly_novosib]

    absolut_calibration = calculate_calibration_coef(fibers, ophir_data_path=path_ophir,
                                                     ophir_shot_name=ophir_shot_name,
                                                     p_torr=80, gas_temperature=23)

    with open('absolute_calib_05_24.json', 'w') as file:
        json.dump(absolut_calibration, file, indent=4)
