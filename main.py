from pathlib import Path

from utils.diagnostic_utils import LaserNdYag
from utils.path_parser import read_config
from utils.POLY_v2 import built_fibers, calculate_Te_ne
from utils.write_files import write_results


def main(discharge_num):
    # следи за числом выстрелов в обработке, метод гет интегралс в полихроматоре

    config_Path = Path("PATH.ini")
    config = read_config(config_Path)

    laser = LaserNdYag(laser_wl=1064.4e-9, laser_energy=1.5)
    laser_shots_times, fibers = built_fibers(discharge_num, config, laser=laser)

    # calculate_Te_ne(fibers)

    for fiber in fibers[:2]:
        print(fiber.gain.resulting_multiplier, fiber.poly_name)
        # fiber.plot_raw_signals(from_shot=0, to_shot=20)

    # write_results(discharge_num, config['save_data_path'], laser_shots_times, fibers)


if __name__ == "__main__":
    discharges = [
        "44639",
        "44626",
        "44640",
        "44627",
        "44629",
        "44630",
        "44631",
        "44632",
        "44633",
        "44634",
    ]
    # discharges = ['44515', '44579']
    discharges = [44644]
    try:
        for discharge in discharges:
            main(discharge)
    except Exception:
        pass
