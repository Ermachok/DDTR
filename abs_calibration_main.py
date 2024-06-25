import json
from pathlib import Path

from utils.path_parser import read_config
from utils.POLY_v2 import built_fibers
from utils.calibration_utils import calculate_calibration_coef

if __name__ == '__main__':
    laser_shot_num = '00913'
    ophir_shot_name = '75_18.txt'

    config_Path = Path(r'PATH.ini')
    config = read_config(config_Path)

    combiscope_times, fibers = built_fibers(laser_shot_num, config, calibration_flag=True)

    absolut_calibration = calculate_calibration_coef(fibers, ophir_data_path=config['path_ophir_calibration'],
                                                     ophir_shot_name=ophir_shot_name,
                                                     p_torr=80, gas_temperature=23)

    with open('calibrations/calibration_configs/absolute_calib_june2024.json', 'w') as file:
        json.dump(absolut_calibration, file, indent=4)
