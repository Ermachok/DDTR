from pathlib import Path

from utils.path_parser import read_config
from utils.write_files import write_results
from utils.POLY_v2 import built_fibers, calculate_Te_ne



if __name__ == '__main__':

    # следи за числом выстрелов в обработке, метод гет интегралс в полихроматоре
    discharge_num = '44643'
    config_Path = Path('PATH.ini')
    config = read_config(config_Path)

    combiscope_times, fibers = built_fibers(discharge_num, config)
    calculate_Te_ne(fibers)

    laser_shots_times = combiscope_times

    # for fiber in fibers:
    #     fiber.plot_raw_signals(from_shot=0, to_shot=10)

    write_results(discharge_num, config['save_data_path'], laser_shots_times, fibers)
