from pathlib import Path

from utils.path_parser import read_config
from utils.write_files import write_results
from utils.POLY_v2 import built_fibers, calculate_Te_ne
from utils.diagnostic_utils import LaserNdYag


def main(discharge_num):
    # следи за числом выстрелов в обработке, метод гет интегралс в полихроматоре

    config_Path = Path('PATH.ini')
    config = read_config(config_Path)

    laser = LaserNdYag(laser_wl=1064.4E-9, laser_energy=1.5)
    laser_shots_times, fibers = built_fibers(discharge_num, config, laser=laser)

    calculate_Te_ne(fibers)

    # for fiber in fibers:
    #     fiber.plot_raw_signals(from_shot=0, to_shot=10)

    write_results(discharge_num, config['save_data_path'], laser_shots_times, fibers)


if __name__ == '__main__':
    discharge = '44581'
    main(discharge)
