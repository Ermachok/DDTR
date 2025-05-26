import os
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import matplotlib.pyplot as plt

# Constants for file paths
INITIAL_PATH_TO_MCC = r'C:\TS_data\experimental_data\mcc_data'
INITIAL_PATH_TO_DTR_DATA = r'C:\TS_data\processed_shots'
INITIAL_PATH_IR_CAMERA = r'C:\TS_data\IR_data\Result_Temperature'
INITIAL_PATH_TO_EQUATORTS_DATA = r'C:\TS_data\equator_TS_data'
INITIAL_PATH_EQUILIBRIUM_DATA = r'C:\TS_data\Kiselev_magnetic_equilibrium'


def find_nearest(array: np.ndarray, value: float, out_value: bool = False, out_index: bool = False) -> Union[
    int, float, Tuple[int, float]]:
    """
    Find the index and/or value in `array` that is closest to `value`.

    Args:
        array (np.ndarray): The array to search.
        value (float): The value to find.
        out_value (bool): Whether to return the closest value.
        out_index (bool): Whether to return the index of the closest value.

    Returns:
        Union[int, float, Tuple[int, float]]: Depending on `out_value` and `out_index`.
    """
    idx = (np.abs(array - value)).argmin()
    if out_index and out_value:
        return idx, array[idx]
    elif out_index:
        return idx
    elif out_value:
        return array[idx]
    else:
        raise ValueError('No output flag specified in find_nearest function')


def get_divertor_data(shot_number: Union[str, int]) -> Optional[Dict]:
    """
    Retrieve divertor data for a given shot number.

    Args:
        shot_number (Union[str, int]): The shot number.

    Returns:
        Optional[Dict]: A dictionary containing the divertor data, or None if an error occurs.
    """
    path = os.path.join(INITIAL_PATH_TO_DTR_DATA, str(shot_number))
    try:
        files = os.listdir(path)
        coordinates = []
        times = []
        ne_all = []
        ne_err_all = []
        Te_all = []
        Te_err_all = []

        for file_name in files:
            if 'ne' in file_name:
                with open(os.path.join(path, file_name)) as ne_file:
                    ne_file_data = ne_file.readlines()

                for ind, line in enumerate(ne_file_data):
                    if ind == 0:
                        times = [float(t) for t in line.split(',')[1::2]]
                    elif ind > 0:
                        line_data = line.split(', ')
                        coordinates.append(float(line_data[0]) / 100)  # Convert cm to m
                        ne_all.append([float(n) for n in line_data[1::2]])
                        ne_err_all.append([float(n_err) for n_err in line_data[2::2]])

            elif 'Te' in file_name:
                with open(os.path.join(path, file_name)) as te_file:
                    te_file_data = te_file.readlines()

                for ind, line in enumerate(te_file_data):
                    if ind > 0:
                        line_data = line.split(', ')
                        Te_all.append([float(t) for t in line_data[1::2]])
                        Te_err_all.append([float(t_err) for t_err in line_data[2::2]])

        return {
            'discharge': shot_number,
            'times_ms': times,
            'Z_m': coordinates,
            'ne(t)': ne_all,
            'ne_err(t)': ne_err_all,
            'Te(t)': Te_all,
            'Te_err(t)': Te_err_all
        }

    except Exception as e:
        print(f'Error in getting DTS data: {e}')
        return None


def get_equator_data(shot_num: Union[int, str]) -> Optional[Dict]:
    """
    Retrieve equator data for a given shot number.

    Args:
        shot_num (Union[int, str]): The shot number.

    Returns:
        Optional[Dict]: A dictionary containing the equator data, or None if an error occurs.
    """
    full_path = os.path.join(INITIAL_PATH_TO_EQUATORTS_DATA, str(shot_num))
    try:
        files = os.listdir(full_path)
        coordinates = []
        times = []
        ne_data = {}
        te_data = {}
        ne_err_data = {}
        te_err_data = {}

        for file in files:
            if file == f'{shot_num}_n(t).csv':
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

            elif file == f'{shot_num}_T(t).csv':
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


def get_magnetic_equilibrium_data(shot_num: Union[int, str], time: float) -> Optional[Dict]:
    """
    Retrieve magnetic equilibrium data for a given shot number and time.

    Args:
        shot_num (Union[int, str]): The shot number.
        time (float): The time in milliseconds.

    Returns:
        Optional[Dict]: A dictionary containing the magnetic equilibrium data, or None if an error occurs.
    """
    full_path = os.path.join(INITIAL_PATH_EQUILIBRIUM_DATA, str(shot_num))
    time_formatted = str(time)[:-2]
    data_prefix = 'psi'
    r_name_pattern = 'r2d'
    z_name_pattern = 'z2d'

    try:
        files = os.listdir(full_path)
        z_data = []
        r_data = []
        psi_data = []

        for file in files:
            if z_name_pattern in file and time_formatted in file:
                with open(os.path.join(full_path, file)) as z_file:
                    z_data = [float(z) for z in z_file.readline().split(' ')]
            elif r_name_pattern in file and time_formatted in file:
                with open(os.path.join(full_path, file)) as r_file:
                    r_data = [float(line.split(' ')[0]) for line in r_file.readlines()]
            elif data_prefix in file and time_formatted in file:
                with open(os.path.join(full_path, file)) as psi_file:
                    psi_data = [line.split(' ') for line in psi_file.readlines()]

        return {
            'z_m': z_data,
            'r_m': r_data,
            'psi': psi_data
        }

    except Exception as e:
        print(f'Error in getting magnetic equilibrium data: {e}')
        return None


def prepare_data_for_poloidal_plot(ts_data: List[Dict], equilibrium: Dict) -> Tuple:
    """
    Prepare data for poloidal plot by calculating psi values and errors.

    Args:
        ts_data (List[Dict]): The TS data.
        equilibrium (Dict): The magnetic equilibrium data.

    Returns:
        Tuple: A tuple containing psi values and corresponding data.
    """
    ts_te = [point['Te'] for point in ts_data]
    ts_ne = [point['ne'] for point in ts_data]
    ts_nt = [T * n for T, n in zip(ts_te, ts_ne)]

    ts_te_err = [point['Te_err'] for point in ts_data]
    ts_ne_err = [point['ne_err'] for point in ts_data]
    ts_nt_err = [(te_err / te + ne_err / ne) * ne * te if te != 0 and ne != 0 else 0
                 for te_err, te, ne_err, ne in zip(ts_te_err, ts_te, ts_ne_err, ts_ne)]

    psi_ts = []
    for point in ts_data:
        z_idx = find_nearest(np.array(equilibrium['z_m']), point['z_m'], out_index=True)
        r_idx = find_nearest(np.array(equilibrium['r_m']), point['r_m'], out_index=True)
        psi_ts.append(float(equilibrium['psi'][r_idx][z_idx]) ** 0.5)

    return psi_ts, ts_ne, ts_te, ts_nt, ts_ne_err, ts_te_err, ts_nt_err


def plot_data_from_psi(ets_data: List[Dict], dts_data: List[Dict], equilibrium_data: Dict):
    """
    Plot data as a function of psi.

    Args:
        ets_data (List[Dict]): The ETS data.
        dts_data (List[Dict]): The DTS data.
        equilibrium_data (Dict): The magnetic equilibrium data.
    """
    psi_ets, ets_ne, ets_te, ets_nt, ets_ne_err, ets_te_err, ets_nt_err = prepare_data_for_poloidal_plot(ets_data,
                                                                                                         equilibrium_data)
    psi_dts, dts_ne, dts_te, dts_nt, dts_ne_err, dts_te_err, dts_nt_err = prepare_data_for_poloidal_plot(dts_data,
                                                                                                         equilibrium_data)

    psi_dts_sorted = sorted(psi_dts)
    dts_ne = [dts_ne[psi_dts.index(value)] for value in psi_dts_sorted]
    dts_te = [dts_te[psi_dts.index(value)] for value in psi_dts_sorted]
    dts_nt = [dts_nt[psi_dts.index(value)] for value in psi_dts_sorted]
    dts_ne_err = [dts_ne_err[psi_dts.index(value)] for value in psi_dts_sorted]
    dts_te_err = [dts_te_err[psi_dts.index(value)] for value in psi_dts_sorted]

    fig, axs = plt.subplots(1, 3, figsize=(15, 5))

    axs[0].errorbar(psi_ets, ets_ne, yerr=ets_ne_err, fmt='o-', markersize=3, label=f'ne, ETS {time}')
    axs[0].errorbar(psi_dts_sorted, dts_ne, yerr=dts_ne_err, fmt='o', markersize=3, label=f'ne, DTS {time}')
    axs[0].set_ylabel('$n_e, m^{-3}$', fontsize=16)
    axs[0].set_xlabel('$\psi$', fontsize=16)

    axs[1].errorbar(psi_ets, ets_te, yerr=ets_te_err, fmt='o-', markersize=3, label=f'Te, ETS {time}')
    axs[1].errorbar(psi_dts_sorted, dts_te, yerr=dts_te_err, fmt='o', markersize=3, label=f'Te, DTS {time}')
    axs[1].set_ylabel('Te')
    axs[1].set_xlabel('$\psi$', fontsize=16)

    axs[2].errorbar(psi_ets, ets_nt, yerr=ets_nt_err, fmt='o-', markersize=3, label=f'ne*Te, ETS {time}')
    axs[2].errorbar(psi_dts_sorted, dts_nt, yerr=dts_nt_err, fmt='o', markersize=3, label=f'ne*Te, DTS {time}')
    axs[2].set_ylabel('ne * Te')

    for ax in axs:
        ax.grid()
        ax.legend()

    plt.show()


if __name__ == '__main__':
    shot_num = 44644
    dts_data = get_divertor_data(shot_num)
    equator_data = get_equator_data(shot_num)

    if dts_data and equator_data:
        for time in [160.6]:
            equilibrium_data = get_magnetic_equilibrium_data(shot_num, time)
            if equilibrium_data:
                dts_time_idx, nearest_dts_shot = find_nearest(np.array(dts_data['times_ms']), time, out_value=True,
                                                              out_index=True)
                nearest_ets_shot = find_nearest(np.array(equator_data['times_ms']), time, out_value=True)

                dts_points = [{
                    'r_m': 0.24,
                    'z_m': z,
                    'ne': ne[dts_time_idx],
                    'Te': Te[dts_time_idx],
                    'ne_err': ne_err[dts_time_idx],
                    'Te_err': Te_err[dts_time_idx]
                } for z, ne, Te, ne_err, Te_err in
                    zip(dts_data['Z_m'], dts_data['ne(t)'], dts_data['Te(t)'], dts_data['ne_err(t)'],
                        dts_data['Te_err(t)'])]

                equator_points = [{
                    'r_m': r,
                    'z_m': 0,
                    'ne': equator_data['ne'][nearest_ets_shot][i],
                    'Te': equator_data['Te'][nearest_ets_shot][i],
                    'ne_err': equator_data['ne_err'][nearest_ets_shot][i],
                    'Te_err': equator_data['Te_err'][nearest_ets_shot][i]
                } for i, r in enumerate(equator_data['R_m'])]

                plot_data_from_psi(equator_points, dts_points, equilibrium_data)
