from pathlib import Path
import os
import configparser


def read_config(config_path: Path):
    config = configparser.ConfigParser()

    config.read(config_path)

    path_calib_experimental_data = config.get('Paths', 'path_calib_experimental_data')
    path_experimental_data = config.get('Paths', 'path_experimental_data')
    path_ophir = config.get('Paths', 'path_ophir')
    ophir_shot_name_end = config.get('Paths', 'ophir_shot_name_end')
    sht_files_path = config.get('Paths', 'path_sht_files')

    spec_calib_filename = config.get('path_spectral_calibration', 'spec_calib_filename')
    path_spectral_calibration = config.get('path_spectral_calibration', 'path')

    abs_calib_filename = config.get('path_absolute_calibration', 'abs_calib_filename')
    path_absolute_calibration = config.get('path_absolute_calibration', 'path')

    path_eq_f_exp = config.get('path_eq_f_exp', 'path')
    path_T15_f_exp = config.get('path_T15_f_exp', 'path')


    config_connection = config.get('poly_fiber_caen_connection', 'path')
    save_data = config.get('save_data_path', 'path')


    config_data = {
        'path_calib_experimental_data': Path(path_calib_experimental_data),
        'path_experimental_data': Path(path_experimental_data),
        'path_ophir': Path(path_ophir),
        'ophir_shot_name_end': Path(ophir_shot_name_end),
        'sht_files_path': Path(sht_files_path),

        'path_spectral_calibration': os.path.join(path_spectral_calibration,spec_calib_filename),
        'path_absolute_calibration': os.path.join(path_absolute_calibration,abs_calib_filename),

        'path_eq_f_exp': Path(path_eq_f_exp),
        'path_T15_f_exp': Path(path_T15_f_exp),

        'poly_fiber_caen_connection': Path(config_connection),
        'save_data_path': Path(save_data)
    }

    return config_data
