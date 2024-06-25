import random
import matplotlib.pyplot as plt


initial_path_to_mcc = r'C:\Users\NE\Desktop\DTR_data\mcc_data'


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
        ax.set_ylim(-0.5, 0.5)
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
        axs[ax_ind][0].set_xlim(420, 600)


def draw_phe(z_pos, timestamp, ch_data: list, ax, add_flag: bool = False):

    if not add_flag:
        ax.clear()

    channels_num = [1 + i for i in range(len(ch_data))]

    ax.plot(channels_num, ch_data, '-*', label=f'{z_pos} cm, {timestamp} ms')
    ax.set_ylim(0, max(ch_data) * 1.1)
    ax.set_xticks(channels_num)
    ax.legend()
