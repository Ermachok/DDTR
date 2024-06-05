import json
from pathlib import Path
import os

from utils.POLY_v2 import Polychromator
from utils.caen_handler import handle_all_caens_multiproces
from utils.gains import GainsEquator, Gains_T15_34, Gains_T15_35
from utils.get_SHT_data import get_DTRlaser_times
from utils.path_parser import read_config
from utils.write_files import write_results


discharge_num = '44648'
config_Path = Path('PATH.ini')
config = read_config(config_Path)


if __name__ == '__main__':
    with open(config['poly_fiber_caen_connection']) as file:
        config_connection = json.load(file)

    laser_shots_times = get_DTRlaser_times(int(discharge_num), config['sht_files_path'])

    msg_list = [0, 1, 2, 3]
    all_caens = handle_all_caens_multiproces(discharge_num=discharge_num, path=config['path_experimental_data'],
                                             msg_list=msg_list, processed_shots=30)

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

    for fiber in fibers:
        fiber.get_temperatures(print_flag=False)
        fiber.get_density(print_flag=False)
        fiber.get_errors()

    write_results(discharge_num, config['save_data_path'], laser_shots_times, fibers)
