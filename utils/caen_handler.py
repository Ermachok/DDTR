import multiprocessing as mp
import sys
import time
from pathlib import Path

import msgpack


def caen_msg_handler(
    path, t_step=0.325, time_shift=100, processed_shots: int | str = 30
):
    """
    :param time_shift: сдвиг для построения в одной системе координат
    :param path:путь до файла
    :param t_step: шаг оцифровщика
    :param noise_len: длина для вычисления уровня над нулем и уровня шума
    :param processed_shots: количество обработанных выстрелов
    :return:
    """

    times = []
    caen = []
    caen_channels_number = 16
    with path.open(mode="rb") as file:
        data = msgpack.unpackb(file.read())

    if str(processed_shots).lower() == "all":
        processed_shots = len(data)

    combiscope_times = []
    for caen_channel in range(caen_channels_number):
        caen_ch = []
        for laser_shot in range(processed_shots):
            if caen_channel == 0:
                combiscope_times.append(round(data[laser_shot]["t"] - data[0]["t"], 3))
            signal = data[laser_shot]["ch"][caen_channel]
            caen_ch.append(signal)
        caen.append(caen_ch)

    for laser_shot in range(processed_shots):
        max_position_ind = caen[0][laser_shot].index(max(caen[0][laser_shot]))
        time = [time_shift - (max_position_ind - t) * t_step for t in range(1024)]
        times.append(time)

    return combiscope_times[1:], times, caen  # [1:] - первый нулевой запуск опускаю


def handle_all_caens(
    discharge_num: str, path: str, processed_shots: int | str
) -> (list, list):
    msg_files_num_x10 = [0, 1, 2, 3]

    all_caens = []
    combiscope_times = []
    for msg_num in msg_files_num_x10:
        new_path = Path(f"{path}/{discharge_num}/{str(msg_num)}.msgpk")
        combiscope_times, times, caen_data = caen_msg_handler(
            new_path, processed_shots=processed_shots
        )
        all_caens.append(
            {"caen_num": msg_num, "shots_time": times, "caen_channels": caen_data}
        )

    return {"combiscope_times": combiscope_times, "caens_data": all_caens}


def handle_one_caen(args):
    discharge_num, path, msg_num, processed_shots = args
    new_path = Path(rf"{path}\{discharge_num}\{msg_num}.msgpk")
    combiscope_times, times, caen_data = caen_msg_handler(
        new_path, processed_shots=processed_shots
    )
    caen_num = msg_num
    return {
        "caen_num": caen_num,
        "shots_time": times,
        "caen_channels": caen_data,
        "combiscope_times": combiscope_times,
    }


def handle_all_caens_multiproces(
    discharge_num: str, path: str, msg_list: list, processed_shots: int | str
) -> list:
    """
    Multiprocess script_DTS
    :param discharge_num:
    :param path:
    :param msg_list:
    :param processed_shots:
    :return:
    """
    args_list = [
        (discharge_num, path, msg_num, processed_shots) for msg_num in msg_list
    ]
    with mp.Pool() as pool:
        results = pool.map(handle_one_caen, args_list)
    all_caens = [result for result in results]
    return all_caens


if __name__ == "__main__":
    for i in range(10):
        start = time.time()
        discharge_number = "44644"
        path_data = r"C:\TS_data\experimental_data\DTS_may_2024"
        all_caens = handle_all_caens(
            discharge_num=discharge_number, path=path_data, processed_shots=30
        )
        msg_list = [0, 1, 2, 3]
        all_caens_2 = handle_all_caens_multiproces(
            discharge_num=discharge_number,
            path=path_data,
            msg_list=msg_list,
            processed_shots="all",
        )

        print(time.time() - start)
