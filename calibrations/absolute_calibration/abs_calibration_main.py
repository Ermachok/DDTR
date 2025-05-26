import json
from pathlib import Path

from utils.calibration_utils import calculate_calibration_coef
from utils.path_parser import read_config
from utils.POLY_v2 import built_fibers

if __name__ == "__main__":
    discharge_num = "00914"
    config_Path = Path(r"C:\Users\NE\PycharmProjects\DDTS\PATH.ini")
    config = read_config(config_Path)

    path_ophir = "C:\TS_data\calibration_data\may2024\Ophir_data"
    ophir_shot_name = "534475_19.txt"

    combiscope_times, fibers = built_fibers(
        discharge_num, config, calibration_flag=True
    )

    for fiber in fibers[-2:]:
        print(fiber.gain.resulting_multiplier, fiber.poly_name)

    absolut_calibration = calculate_calibration_coef(
        fibers,
        ophir_data_path=path_ophir,
        ophir_shot_name=ophir_shot_name,
        p_torr=80,
        gas_temperature=23,
    )

    # with open('absolute_calib_30sep2024.json', 'w') as file:
    #     json.dump(absolut_calibration, file, indent=4)
