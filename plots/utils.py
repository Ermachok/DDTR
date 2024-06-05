import bisect
import json
import random

import matplotlib.pyplot as plt


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


def draw_separatrix(separatrix_data: dict, time: float, shot_num: int,
                    divertor_coords: list = None, equator_radia: list = None, ax=None, add_flag=False):
    if ax is None:
        fig, ax = plt.subplots()

    elif add_flag:
        colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'orange', 'purple', 'brown', 'pink', 'gray']

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
        # fig.gca().set_aspect('equal')

        ax.set_xlim(0.1, 0.625)
        ax.set_ylim(-0.52, 0.5)
        ax.set_aspect('equal')
        ax.legend()
        ax.grid()

    return ax
