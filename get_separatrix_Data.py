import bisect
import json
import os
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon

initial_path_to_mcc = r'C:\TS_data\experimental_data\mcc_data'
initial_path_to_DTR_data = r'C:\TS_data\processed_shots'
initial_path_ir_camera = r'C:\TS_data\IR_data\Result_Temperature'
initial_path_to_EQUATOR_TS_data = r'C:\TS_data\equator_TS_data'


def piecewise_linear_interpolate(x: list, y: list, x_target: float) -> float:
    x = np.array(x)
    y = np.array(y)

    sorted_indices = np.argsort(x)
    x_sorted = x[sorted_indices]
    y_sorted = y[sorted_indices]

    if len(np.unique(x_sorted)) != len(x_sorted):
        raise ValueError("X should be unique")

    y_target = np.interp(x_target, x_sorted, y_sorted)

    return y_target


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


def get_divertor_data(shot_number):
    path = fr'{initial_path_to_DTR_data}\%d' % int(shot_number)
    try:
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

    except Exception as e:
        print(f'Some exception in getting DTS data {e}')
        return None


def get_equator_data(shot_number: int | str) -> dict:
    """
    Retrieve equator data for a given shot number.

    Args:
        shot_number (Union[int, str]): The shot number.

    Returns:
        Optional[Dict]: A dictionary containing the equator data, or None if an error occurs.
    """
    full_path = os.path.join(initial_path_to_EQUATOR_TS_data, str(shot_number))
    try:
        files = os.listdir(full_path)
        coordinates = []
        times = []
        ne_data = {}
        te_data = {}
        ne_err_data = {}
        te_err_data = {}

        for file in files:
            if file == f'{shot_number}_n(t).csv':
                with open(os.path.join(full_path, file)) as ne_file:
                    ne_file_data = ne_file.readlines()

                for ind, line in enumerate(ne_file_data):
                    if ind == 0:
                        coordinates = [float(t) / 1000 for t in line.split(', ')[1::2]]
                    elif ind > 1:
                        line_data = line.split(', ')
                        time = float(line_data[0])
                        times.append(time)
                        ne_data[time] = [float(ne) if ne != "--" else 0 for ne in line_data[1::2]]
                        ne_err_data[time] = [float(ne_err) if ne_err != "--" else 0 for ne_err in line_data[2::2]]

            elif file == f'{shot_number}_T(t).csv':
                with open(os.path.join(full_path, file)) as te_file:
                    te_file_data = te_file.readlines()

                for ind, line in enumerate(te_file_data):
                    if ind > 1:
                        line_data = line.split(', ')
                        time = float(line_data[0])
                        te_data[time] = [float(te) if te != "--" else 0 for te in line_data[1::2]]
                        te_err_data[time] = [float(te_err) if te_err != "--" else 0 for te_err in line_data[2::2]]

        return {
            'R_m': coordinates,
            'Z': 0,
            'times_ms': times,
            'ne': ne_data,
            'ne_err': ne_err_data,
            'Te': te_data,
            'Te_err': te_err_data
        }

    except Exception as e:
        print(f'Error in getting equator data: {e}')
        return None


def get_separatrix_data(path: str, timestamp_base: float) -> dict:
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


def draw_distance_from_separatrix(dts_data: dict, equator_data: dict, mcc_data: dict, timestamp: float):
    index_equator_time = find_nearest(timestamp, equator_data['times_ms'])
    nearest_equator_time = equator_data['times_ms'][index_equator_time]
    ne_equator = equator_data['ne'][nearest_equator_time]
    te_equator = equator_data['Te'][nearest_equator_time]

    ne_equator_err = equator_data['ne_err'][nearest_equator_time]
    Te_equator_err = equator_data['Te_err'][nearest_equator_time]

    equator_points = [(R, 0) for R in equator_data['R_m']]
    equator_distances = find_minimal_distance_to_separatrix(equator_points, mcc_data)

    index_dts_time = find_nearest(timestamp, dts_data['t'])

    ne_dts = []
    ne_dts_err = []
    for point in dts_data['ne(t)']:
        ne_dts.append(point[index_dts_time])
    for point in dts_data['ne_err(t)']:
        ne_dts_err.append(point[index_dts_time])

    te_dts = []
    te_dts_err = []
    for point in dts_data['Te(t)']:
        te_dts.append(point[index_dts_time])
    for point in dts_data['Te_err(t)']:
        te_dts_err.append(point[index_dts_time])

    dts_points = [(0.24, float(Z) / 100) for Z in dts_data['Z']]  # 0.24 R=24 cm diagnostic DTS laser path
    dts_distances = find_minimal_distance_to_separatrix(dts_points, mcc_data)

    fig, axs = plt.subplots(1, 3, figsize=(15, 5))

    print(timestamp, piecewise_linear_interpolate(equator_distances, ne_equator, 0))

    axs[0].errorbar(equator_distances, ne_equator, yerr=ne_equator_err, fmt='o-', label=f'eqTS, {nearest_equator_time}')
    axs[0].errorbar(dts_distances, ne_dts, yerr=ne_dts_err, fmt='o-', label=f'DTS, {dts_data['t'][index_dts_time]}')

    axs[0].set_ylabel('ne')
    axs[0].set_xlabel('Distance to sep, cm')
    axs[0].legend()
    axs[0].grid()

    axs[1].errorbar(equator_distances, te_equator, yerr=Te_equator_err, fmt='o-', label=f'eqTS, {nearest_equator_time}')
    axs[1].errorbar(dts_distances, te_dts, yerr=te_dts_err, fmt='o-', label=f'DTS, {dts_data['t'][index_dts_time]}')

    axs[1].set_ylabel('Te')
    axs[1].set_xlabel('Distance to separatrix, cm')
    axs[1].legend()
    axs[1].grid()

    axs[2].plot(equator_distances, [te * ne for te, ne in zip(te_equator, ne_equator)], 'o-')
    axs[2].plot(dts_distances, [te * ne for te, ne in zip(te_dts, ne_dts)], 'o-')
    axs[2].set_ylabel('ne * Te')
    axs[2].set_xlabel('Distance to separatrix, cm')
    axs[2].grid()

    plt.tight_layout()
    plt.show()


def data_on_separatrix(dts_data: dict, equator_data: dict, mcc_data: dict, timestamp: float):
    index_equator_time = find_nearest(timestamp, equator_data['times_ms'])
    nearest_equator_time = equator_data['times_ms'][index_equator_time]
    ne_equator = equator_data['ne'][nearest_equator_time]
    te_equator = equator_data['Te'][nearest_equator_time]

    ne_equator_err = equator_data['ne_err'][nearest_equator_time]
    Te_equator_err = equator_data['Te_err'][nearest_equator_time]

    equator_points = [(R, 0) for R in equator_data['R_m']]
    equator_distances = find_minimal_distance_to_separatrix(equator_points, mcc_data)

    index_dts_time = find_nearest(timestamp, dts_data['t'])

    ne_dts = []
    ne_dts_err = []
    for point in dts_data['ne(t)']:
        ne_dts.append(point[index_dts_time])
    for point in dts_data['ne_err(t)']:
        ne_dts_err.append(point[index_dts_time])

    te_dts = []
    te_dts_err = []
    for point in dts_data['Te(t)']:
        te_dts.append(point[index_dts_time])
    for point in dts_data['Te_err(t)']:
        te_dts_err.append(point[index_dts_time])

    dts_points = [(0.24, float(Z) / 100) for Z in dts_data['Z']]  # 0.24 R=24 cm diagnostic DTS laser path
    dts_distances = find_minimal_distance_to_separatrix(dts_points, mcc_data)

    # print(timestamp, max(ne_dts), piecewise_linear_interpolate(equator_distances, ne_equator, 0))
    # print(te_dts[ne_dts.index(max(ne_dts))], piecewise_linear_interpolate(equator_distances, te_equator, 0))
    print(te_dts[ne_dts.index(max(ne_dts))], max(te_equator))


def find_minimal_distance_to_separatrix(points: list[set], mcc_data: dict):
    R_sep = mcc_data['body']['R']
    Z_sep = mcc_data['body']['Z']

    if (R_sep[0], Z_sep[0]) != (R_sep[-1], Z_sep[-1]):
        R_sep.append(R_sep[0])
        Z_sep.append(Z_sep[0])

    polygon_coords = list(zip(R_sep, Z_sep))
    polygon = Polygon(polygon_coords)

    all_distances = []
    for point in points:
        point_object = Point(point)

        if polygon.contains(point_object):
            min_distance = -point_object.distance(polygon.exterior)
        else:
            min_distance = point_object.distance(polygon)

        all_distances.append(min_distance * 100)  # meters to cm

    return all_distances


if __name__ == '__main__':
    sht_nums = [44612, 44613, 44637, 44642, 44643, 44644, 44648, 44649, 44639, 44640, 44626, 44627, 44630,
                44631, 44632, 44633, 44634]
    timestamps = [170.6, 180.6, 190.6, 200.6, 210.6]

    for sht_num in sht_nums:
        # print(sht_num, '\n')
        path_to_mcc = f'{initial_path_to_mcc}/mcc_{sht_num}.json'

        dts_data = get_divertor_data(shot_number=sht_num)
        equator_data = get_equator_data(shot_number=sht_num)

        try:
            for timestamp in timestamps:
                sep_data = get_separatrix_data(path=path_to_mcc, timestamp_base=timestamp)

                data_on_separatrix(dts_data, equator_data, sep_data, timestamp)
                # draw_distance_from_separatrix(dts_data, equator_data, sep_data, timestamp)
        except Exception:
            continue
