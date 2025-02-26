import random
import bisect
import matplotlib.pyplot as plt
from gui.utils_gui import find_nearest, find_minimal_distance_to_separatrix


def draw_separatrix(separatrix_data: dict, time: float, shot_num: int,
                    divertor_coords: list = None, equator_radia: list = None, ax=None, add_flag=False):
    if ax is None:
        fig, ax = plt.subplots()

    elif add_flag:
        colors = ['g', 'r', 'c', 'm', 'y', 'k', 'orange', 'purple', 'brown', 'pink', 'gray']
        color = random.choice(colors)

        ax.plot(separatrix_data['body']['R'], separatrix_data['body']['Z'], color, label=time)
        ax.plot(separatrix_data['leg_1']['R'], separatrix_data['leg_1']['Z'], color)
        ax.plot(separatrix_data['leg_2']['R'], separatrix_data['leg_2']['Z'], color)
        ax.legend()

    else:
        ax.clear()

        for point in divertor_coords:
            ax.scatter(0.24, float(point) / 100, c='red', zorder=10, s=5)

        for point in equator_radia:
            ax.scatter(point, 0, c='green', zorder=10, s=5)

        ax.plot(separatrix_data['body']['R'], separatrix_data['body']['Z'], '-b', label=time)
        ax.plot(separatrix_data['leg_1']['R'], separatrix_data['leg_1']['Z'], '-b')
        ax.plot(separatrix_data['leg_2']['R'], separatrix_data['leg_2']['Z'], '-b')

        ax.set_title(f'{shot_num}, time: {time}')

        ax.set_xlim(0.1, 0.625)
        ax.set_ylim(-0.51, 0.03)
        ax.set_aspect('equal')
        ax.legend()
        ax.grid()

    return ax


def draw_raw_signals(z_pos, timestamp, fiber_data: list, axs, add_flag: bool = False):
    for ax in axs.flat:
        if not add_flag:
            ax.clear()

    counts = [i for i in range(1024)]

    for ch, ch_data in enumerate(fiber_data):
        axs[ch][0].plot(counts, ch_data, label=f' {z_pos} cm, {timestamp} ms')

    for ax_ind in range(4):
        axs[ax_ind][0].legend()
        #axs[ax_ind][0].set_xlim(420, 600)


def draw_phe(z_pos, timestamp, ch_data: list, ax, add_flag: bool = False):

    if not add_flag:
        ax.clear()

    channels_num = [1 + i for i in range(len(ch_data))]
    ax.plot(channels_num, ch_data, '-*', label=f'{z_pos} cm, {timestamp} ms')
    ax.set_ylim(0, max(ch_data) * 1.1)
    ax.set_xticks(channels_num)
    ax.legend()


def draw_ir_camera(shot_num: str, ir_data: dict, ax):
    ax.set_xlabel('R')
    ax.set_ylabel('Temperature')

    ax.plot(ir_data['radii'], [0 for _ in range(len(ir_data['radii']))],
                    label=shot_num)


def draw_expected(fe_data: dict, ax, phe_data: list, timestamp, add_flag: bool = False):
    """

    :param fe_data:
    :param ax:
    :param phe_data: list of number of phe for each channel
    :param add_flag:
    :return:
    """

    if not add_flag:
        ax.clear()

    all_channels = {f'{idx_ch + 1}': [] for idx_ch in range(len(fe_data['1.0']))}
    Te_grid = fe_data['Te_grid']
    for index,  f_e in enumerate(fe_data.values()):
        if index > 1:
            for idx_ch, value in enumerate(f_e):
                all_channels[f'{idx_ch + 1}'].append(value)

    ch1_to_ch2 = [ch1/ch2 for ch1, ch2 in zip(all_channels['1'], all_channels['2'])]
    ch1_to_ch3 = [ch1/ch3 for ch1, ch3 in zip(all_channels['1'], all_channels['3'])]

    phe1_to_phe2 = phe_data[0]/phe_data[1]
    phe1_to_phe3 = phe_data[0]/phe_data[2]

    index_1 = find_nearest(ch1_to_ch2, phe1_to_phe2)
    index_2 = find_nearest(ch1_to_ch3, phe1_to_phe3)

    ax.scatter(Te_grid[index_1], phe1_to_phe2, label=f'ch1/ch2, {timestamp}')
    ax.scatter(Te_grid[index_2], phe1_to_phe3, label=f'ch1/ch3, {timestamp}')

    ax.plot(Te_grid, ch1_to_ch2, label='ch1_exp / ch2_exp')
    ax.plot(Te_grid, ch1_to_ch3, label='ch1_exp / ch3_exp')

    ax.set_xlim([0, 150])
    ax.set_ylim([0, 20])
    ax.legend()


def draw_distance_from_separatrix(dts_data: dict, equator_data: dict, mcc_data: dict, timestamp: float):
    index_equator_time = find_nearest(timestamp, equator_data['times'])
    nearest_equator_time = equator_data['times'][index_equator_time]
    ne_equator = equator_data['ne'][nearest_equator_time]
    te_equator = equator_data['Te'][nearest_equator_time]

    equator_points = [(R, 0) for R in equator_data['R_m']]
    equator_distances = find_minimal_distance_to_separatrix(equator_points, mcc_data)

    index_dts_time = find_nearest(timestamp, dts_data['t'])

    ne_dts = []
    for point in dts_data['ne(t)']:
        ne_dts.append(point[index_dts_time])

    te_dts = []
    for point in dts_data['Te(t)']:
        te_dts.append(point[index_dts_time])

    dts_points = [(0.24, float(Z)/100) for Z in dts_data['Z']]   # 0.24 R=24 cm diagnostic DTS laser path
    dts_distances = find_minimal_distance_to_separatrix(dts_points, mcc_data)

    fig, axs = plt.subplots(1, 3)
    axs[0].plot(equator_distances, ne_equator, 'o-', label=f'eqTS, {nearest_equator_time}')
    axs[0].plot(dts_distances, ne_dts, 'o-', label=f'DTS, {dts_data['t'][index_dts_time]}')

    # axs[0].set_xlim(min(dts_distances) * 1.1 if min(dts_distances) < 0 else min(dts_distances)/1.1,
    #                 max(dts_distances) * 1.1)
    # #axs[0].set_ylim(0, max(ne_dts) * 2)

    axs[0].set_ylabel('ne')
    axs[0].set_xlabel('Distance to sep, cm')
    axs[0].legend()
    axs[0].grid()

    axs[1].plot(equator_distances, te_equator, 'o-', label=f'eqTS, {nearest_equator_time}')
    axs[1].plot(dts_distances, te_dts, 'o-', label=f'DTS, {dts_data['t'][index_dts_time]}')
    # axs[1].set_xlim(min(dts_distances) * 1.2 if min(dts_distances) < 0 else min(dts_distances) / 1.1,
    #                 max(dts_distances) * 1.5)
    #axs[1].set_ylim(0, max(te_dts) * 2)
    axs[1].set_ylabel('Te')
    axs[1].set_xlabel('Distance to separatrix, cm')
    axs[1].legend()
    axs[1].grid()

    axs[2].plot(equator_distances, [te*ne for te, ne in zip(te_equator, ne_equator)] , 'o-')
    axs[2].plot(dts_distances, [te*ne for te, ne in zip(te_dts, ne_dts)], 'o-')
    axs[2].grid()
    # axs[2].set_xlim(min(dts_distances) * 1.2 if min(dts_distances) < 0 else min(dts_distances) / 1.1,
    #                 max(dts_distances) * 1.2)
    #axs[2].set_ylim(0, max([te*ne for te, ne in zip(te_dts, ne_dts)]) * 2)

    fig.show()

