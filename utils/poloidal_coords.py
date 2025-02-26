import os
import numpy as np
import matplotlib.pyplot as plt

initial_path_to_mcc = r'C:\TS_data\experimental_data\mcc_data'
initial_path_to_DTR_data = r'C:\TS_data\processed_shots'
initial_path_ir_camera = r'C:\TS_data\IR_data\Result_Temperature'
initial_path_to_EQUATORTS_data = r'C:\TS_data\equator_TS_data'
initial_path_equilibrium_data = r'C:\TS_data\Kiselev_magnetic_equlibrium'


def find_nearest(array, value,
                 out_value: bool | None = None,
                 out_index: bool | None = None):

    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    if out_index and out_value:
        return idx, array[idx]
    elif out_index:
        return idx
    elif out_value:
        return array[idx]
    else:
        raise UserWarning('There is no flag in find_nearest function')



def get_divertor_data(shot_number: str | int):
    path = fr'{initial_path_to_DTR_data}\{int(shot_number)}'
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
                        coordinate.append(float(line_data_list[0]) / 100)  #100 - cm -> m
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

        return {'discharge': shot_number, 'times_ms': times, 'Z_m': coordinate,
                'ne(t)': ne_all, 'ne_err(t)': ne_err_all,
                'Te(t)': Te_all, 'Te_err(t)': Te_err_all}

    except Exception as e:
        print(f'Some exception in getting DTS data {e}')
        return None


def get_equator_data(shot_num: int | str):
    initial_eq_data = initial_path_to_EQUATORTS_data
    full_path = fr'{initial_eq_data}\{int(shot_num)}'
    try:
        files = os.listdir(full_path)
        coordinates = []
        times = []
        ne_data = {}
        te_data = {}

        ne_err_data = {}
        te_err_data = {}


        for file in files:
            if file == f'{int(shot_num)}_n(t).csv':
                with open(fr'{full_path}\{file}') as ne_file:
                    ne_file_data = ne_file.readlines()

                for ind, line in enumerate(ne_file_data):
                    if ind == 0:
                        coordinates = [float(t)/1000 for t in line.split(', ')[1::2]]
                    if ind > 1:
                        line_data_list = line.split(', ')
                        time = float(line_data_list[0])
                        times.append(time)

                        temp_ne = []
                        temp_ne_err = []
                        for ne, ne_err in zip(line_data_list[1::2], line_data_list[2::2]):
                            try:
                                temp_ne.append(float(ne))
                                temp_ne_err.append(float(ne_err))
                            except ValueError:
                                temp_ne.append(0)
                                temp_ne_err.append(0)

                        ne_data[time] = temp_ne
                        ne_err_data[time] = temp_ne_err

            elif file == f'{int(shot_num)}_T(t).csv':
                with open(fr'{full_path}\{file}') as ne_file:
                    ne_file_data = ne_file.readlines()

                for ind, line in enumerate(ne_file_data):
                    if ind > 1:
                        line_data_list = line.split(', ')
                        time = float(line_data_list[0])
                        line_data_list = line.split(', ')
                        temp_te = []
                        temp_te_err = []
                        for te, te_err in zip(line_data_list[1::2], line_data_list[2::2]):
                            try:
                                temp_te.append(float(te))
                                temp_te_err.append(float(te_err))
                            except ValueError:
                                temp_te.append(0)
                                temp_te_err.append(0)

                        te_data[time] = temp_te
                        te_err_data[time] = temp_te_err

        return {'R_m': coordinates,
                'Z': 0,
                'times_ms': times,
                'ne': ne_data,
                'ne_err': ne_err_data,
                'Te': te_data,
                'Te_err': te_err_data,
                }

    except Exception as e:
        print(f'Some exception {e}')
        return None


def get_magnetic_equilibrium_data(shot_num: int | str, time: float):
    initial_equilibrium_data = initial_path_equilibrium_data
    full_path = fr'{initial_equilibrium_data}\{int(shot_num)}'


    time_formatted = str(time)[:-2]
    data_prefix = 'psi'
    r_name_pattern = 'r2d'
    z_name_pattern = 'z2d'

    try:
        files = os.listdir(full_path)
        for file in files:
            if z_name_pattern in file and time_formatted in file:
                with open(fr"{full_path}\{file}") as z_file:
                    z_data = [float(z) for z in z_file.readlines()[0].split(' ')]
            elif r_name_pattern in file and time_formatted in file:
                with open(fr"{full_path}\{file}") as r_file:
                    r_data_lines = r_file.readlines()
                    r_data = []
                    for line in r_data_lines:
                        r_data.append(float(line.split(' ')[0]))

            elif data_prefix in file and time_formatted in file:
                print(f'used {file}')
                with open(fr"{full_path}\{file}") as psi_file:
                    psi = psi_file.readlines()
                    psi_data = [line.split(' ') for line in psi]

        return {'z_m': z_data,
                'r_m': r_data,
                'psi': psi_data}

    except Exception as e:
        print(f'{e} in getting magnetic equilibrium data')


def prepare_data_for_poloidal_plot(ts_data: dict, equilibrium: dict) -> tuple:
    ts_te = [point['Te'] for point in ts_data]
    ts_ne = [point['ne'] for point in ts_data]
    ts_nt = [T * n for T, n in zip(ts_te, ts_ne)]

    ts_te_err = [point['Te_err'] for point in ts_data]
    ts_ne_err = [point['ne_err'] for point in ts_data]
    #ts_nt_err = [(te_err/te + ne_err/ne) * ne*te for te_err, te, ne_err, ne in zip(ts_te_err, ts_te,
    #                                                                               ts_te_err, ts_ne,)]

    ts_nt_err = []
    for te_err, te, ne_err, ne in zip(ts_te_err, ts_te, ts_te_err, ts_ne):
        if te == 0 or ne == 0:
            ts_nt_err.append(0)
        else:
            ts_nt_err.append((te_err / te + ne_err / ne) * ne * te)

    psi_ts = []
    for point in ts_data:
        z_idx = find_nearest(equilibrium['z_m'], point['z_m'], out_index=True)
        r_idx = find_nearest(equilibrium['r_m'], point['r_m'], out_index=True)
        psi_ts.append(float(equilibrium['psi'][r_idx][z_idx])**0.5)

        if point['z_m'] == 0:
            print(point['z_m'], point['r_m'])
            r_idx_1 = find_nearest(equilibrium['r_m'], point['r_m'] + 0.005, out_index=True)
            r_idx_2 = find_nearest(equilibrium['r_m'], point['r_m'] - 0.005, out_index=True)

            print(float(equilibrium['psi'][r_idx_1][z_idx])**0.5, float(equilibrium['psi'][r_idx_2][z_idx])**0.5)

    return psi_ts, ts_ne, ts_te, ts_nt, ts_ne_err, ts_te_err, ts_nt_err


def plot_data_from_psi(ets_data: list, dts_data: list, equilibrium_data: dict):

    psi_ets, ets_ne, ets_te, ets_nt, ets_ne_err, ets_te_err, ets_nt_err = prepare_data_for_poloidal_plot(ets_data, equilibrium_data)
    psi_dts, dts_ne, dts_te, dts_nt, dts_ne_err, dts_te_err, dts_nt_err = prepare_data_for_poloidal_plot(dts_data, equilibrium_data)

    psi_dts_sorted = sorted(psi_dts)
    for i, value in enumerate(psi_dts_sorted):
        dts_ne[psi_dts.index(value)] = dts_ne[i]
        dts_te[psi_dts.index(value)] = dts_te[i]
        dts_nt[psi_dts.index(value)] = dts_nt[i]
        dts_ne_err[psi_dts.index(value)] = dts_ne_err[i]
        dts_te_err[psi_dts.index(value)] = dts_te_err[i]

    axs[0].errorbar(psi_ets, ets_ne, yerr=ets_ne_err, fmt='o-', markersize=3, label=f'ne, ETS {time}')
    axs[0].errorbar(psi_dts_sorted, dts_ne, yerr=dts_ne_err, fmt='o', markersize=3, label=f'ne, DTS {time}')

    #axs[0].plot(psi_ets, ets_ne, 'o-', label=f'ne, ETS {time}')
    #axs[0].plot(psi_dts, dts_ne, 'o-', label=f'ne, DTS {time}')

    axs[1].errorbar(psi_ets, ets_te, yerr=ets_te_err, fmt='o-', markersize=3, label=f'Te, ETS {time}')
    axs[1].errorbar(psi_dts_sorted, dts_te, yerr=dts_te_err, fmt='o', markersize=3, label=f'Te, DTS {time}')

    axs[2].errorbar(psi_ets, ets_nt, yerr=ets_nt_err, fmt='o-', markersize=3, label=f'ne*Te, ETS {time}')
    axs[2].errorbar(psi_dts_sorted, dts_nt, yerr=dts_nt_err, fmt='o', markersize=3,  label=f'ne*Te, DTS {time}')

    axs[0].set_ylabel('ne')
    axs[1].set_ylabel('Te')
    axs[2].set_ylabel('ne * Te')


    for ax in axs.flat:
        ax.grid()
        #ax.legend()

    #plt.show()


if __name__ == '__main__':
    sht_num = 44644

    dts_data = get_divertor_data(sht_num)
    equator_data = get_equator_data(sht_num)


    fig, axs = plt.subplots(1, 3)

    #for time in [190.6, 180.6, 170.6]:
    for time in [194.6, ]:
        time_to_plot = time
        dts_time_idx, nearest_dts_shot = find_nearest(dts_data['times_ms'], time_to_plot,
                                                      out_value=True,
                                                      out_index=True)

        nearest_ets_shot = find_nearest(equator_data['times_ms'], time_to_plot, out_value=True)

        equilibrium_data = get_magnetic_equilibrium_data(shot_num=sht_num,
                                                         time=time_to_plot)  # list[R: len(100)[Z: len(200)]]

        dts_points = []
        for point in range(len(dts_data['Z_m'])):
            dts_points.append(
                {
                    'r_m': 0.24,
                    'z_m': dts_data['Z_m'][point],
                    'ne': dts_data['ne(t)'][point][dts_time_idx],
                    'Te': dts_data['Te(t)'][point][dts_time_idx],
                    'ne_err': dts_data['ne_err(t)'][point][dts_time_idx],
                    'Te_err': dts_data['Te_err(t)'][point][dts_time_idx]
                }
            )


        equator_points = []
        for point in range(len(equator_data['R_m'])):
            equator_points.append(
                {
                    'r_m': equator_data['R_m'][point],
                    'z_m': 0,
                    'ne': equator_data['ne'][nearest_ets_shot][point],
                    'Te': equator_data['Te'][nearest_ets_shot][point],
                    'ne_err': equator_data['ne_err'][nearest_ets_shot][point],
                    'Te_err': equator_data['Te_err'][nearest_ets_shot][point]
                }
            )

        plot_data_from_psi(ets_data=equator_points, dts_data=dts_points, equilibrium_data=equilibrium_data)

    plt.show()
