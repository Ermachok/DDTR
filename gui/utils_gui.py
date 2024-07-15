import bisect
import json
import os
from pathlib import Path
import numpy as np

from utils.path_parser import read_config
from utils.POLY_v2 import built_fibers, calculate_Te_ne
from utils.diagnostic_utils import LaserNdYag


initial_path_to_mcc = r'C:\TS_data\experimental_data\mcc_data'
initial_path_to_DTR_data = r'C:\TS_data\processed_shots'
initial_path_ir_camera = r'C:\TS_data\IR_data\Result_Temperature'


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


def get_Xpoint(path: str, timestamp_base: float) -> dict:
    with open(path) as json_file:
        mcc_data = json.load(json_file)
        mcc_time = mcc_data['time']['variable']
    ms = timestamp_base
    index_time = bisect.bisect_right(mcc_time, ms / 1000)

    body_r = [x / 100 for x in mcc_data['boundary']['rbdy']['variable'][index_time]]
    body_z = [x / 100 for x in mcc_data['boundary']['zbdy']['variable'][index_time]]

    leg1_r = [x / 100 for x in mcc_data['boundary']['rleg_1']['variable'][index_time]]
    leg1_z = [x / 100 for x in mcc_data['boundary']['zleg_1']['variable'][index_time]]

    leg2_r = [x / 100 for x in mcc_data['boundary']['rleg_2']['variable'][index_time]]
    leg2_z = [x / 100 for x in mcc_data['boundary']['zleg_2']['variable'][index_time]]

    separatrix_data = {'body':
        {
            'R': body_r,
            'Z': body_z},
        'leg_1':
            {
                'R': leg1_r,
                'Z': leg1_z},
        'leg_2':
            {
                'R': leg2_r,
                'Z': leg2_z},
        'timepoint': timestamp_base}

    return separatrix_data


def get_divertor_data(shot_number):

    path = fr'{initial_path_to_DTR_data}\%d' % int(shot_number)
    files = os.listdir(path)
    coordinate = []

    for file_name in files:
        if 'ne' in file_name:
            ne_all = []
            ne_err_all = []
            with open(path + fr'\{file_name}') as ne_file:
                ne_file_data = ne_file.readlines()

            for ind, line in enumerate(ne_file_data):
                ne = []
                ne_err = []
                if ind == 0:
                    times = [float(t) for t in line.split(',')[1::2]]
                if ind > 0:
                    line_data_list = line.split(', ')
                    coordinate.append(line_data_list[0])
                    ne = [float(n) for n in line_data_list[1::2]]
                    ne_err = [float(n_err) for n_err in line_data_list[2::2]]

                    ne_all.append(ne)
                    ne_err_all.append(ne_err)

        elif 'Te' in file_name:
            Te_all = []
            Te_err_all = []
            with open(path + fr'\{file_name}') as te_file:
                te_file_data = te_file.readlines()

            for ind, line in enumerate(te_file_data):
                te = []
                te_err = []
                if ind > 0:
                    line_data_list = line.split(', ')
                    te = [float(t) for t in line_data_list[1::2]]
                    te_err = [float(t_err) for t_err in line_data_list[2::2]]

                    Te_all.append(te)
                    Te_err_all.append(te_err)

    return {'discharge': shot_number, 't': times, 'Z': coordinate,
            'ne(t)': ne_all, 'ne_err(t)': ne_err_all,
            'Te(t)': Te_all, 'Te_err(t)': Te_err_all}


def get_ir_data(shot_num):
    file_path = f'{initial_path_ir_camera}%s.csv' % shot_num

    try:
        with open(file_path, 'r') as data_file:
            data = data_file.readlines()
    except Exception:
        raise FileNotFoundError

    result = {
        'times_ms': [],
        'radii': [],
    }
    for ind, line in enumerate(data):
        line_data_list = line.split(',')
        if ind == 0:
            times = [float(time) for time in line_data_list[1:]]
            result['times_ms'] = times
            for time in times:
                result[time] = []
        else:
            result['radii'].append(float(line_data_list[0]))
            for time_ind, temperature in enumerate(line_data_list[1:]):
                result[times[time_ind]].append(float(temperature))

    return result


def get_equator_data(path):
    initial_eq_data = None
    path = fr'{initial_eq_data}\%d' % int(path)
    files = os.listdir(path)
    coordinate = []

    for file in files:
        if 'n(R)' in file:
            with open(path + fr'\{file}') as ne_file:
                ne_file_data = ne_file.readlines()

            for ind, line in enumerate(ne_file_data):
                if ind > 1:
                    line_data_list = line.split(', ')
                    coordinate.append(float(line_data_list[0]) / 1000)
            return {'R': coordinate}


def download_poly_data(discharge_num):
    config_Path = Path("PATH.ini")
    config = read_config(config_Path)

    laser = LaserNdYag(laser_energy=1.5, laser_wl=1064.4E-9)

    combiscope_times, fibers = built_fibers(discharge_num, config, laser=laser)
    calculate_Te_ne(fibers)

    laser_shots_times = combiscope_times

    return laser_shots_times, fibers
