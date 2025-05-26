import logging
from pathlib import Path

import shtRipper

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def log_function_name(func):
    """
    Logging
    :param func:
    :return:
    """

    def wrapper(*args, **kwargs):
        logging.info(f"Function {func.__name__} is called")
        return func(*args, **kwargs)

    return wrapper


@log_function_name
def scan_DTR(sht_data: dict) -> bool:
    """
    Scans DTR measurements(laser shots) in discharge
    :param sht_data: dictionary from shtRipper
    :return: True or False
    """
    if "Лазер ДДТР" in sht_data:
        print("There are DTR measurements")
        return True
    else:
        print("There aren't DTR measurements")
        return False


@log_function_name
def get_DTRlaser_times(
    sht_number: int,
    sht_path: str,
    laser_frequency: int = 100,
    signal_threshold: float = 0.25,
    max_laser_shots_number: int = 23,
) -> tuple:
    """
    Returns DTR laser shots times
    :param sht_path: path to sht files
    :param sht_number: tokamak discharge(shot) number
    :param signal_threshold: signal determination threshold, Volts
    :param laser_frequency: laser frequency, Hz
    :param max_laser_shots_number: maximum number of laser shots
    :return: DTR laser shots times (tuple)
    """
    sht_ext: str = ".SHT"
    filename = Path("%s/sht%05d%s" % (sht_path, sht_number, sht_ext))
    sht_data = shtRipper.ripper.read(filename)

    if scan_DTR(sht_data):
        x_data: list = sht_data["Лазер ДДТР"]["x"]
        y_data: list = sht_data["Лазер ДДТР"]["y"]

        DTR_times = []
        idle_time = 0  # waits for first laser shot
        for time, signal in zip(x_data, y_data):
            if signal > signal_threshold:
                if not DTR_times:
                    DTR_times.append(round(time * 1e3, 2))  # seconds to ms
                    idle_time = (
                        time + 1 / laser_frequency * 0.7
                    )  # seconds, 0.8 - in case laser instability
                elif time < idle_time:
                    pass
                else:
                    DTR_times.append(round(time * 1e3, 2))  # seconds to ms
                    idle_time = time + 1 / laser_frequency * 0.7
                    if (
                        DTR_times[-2] - DTR_times[-1] > 1e3 / laser_frequency * 1.2
                    ):  # 1.2 - in case laser instability
                        print("Alarm, suspicious laser shots found")

                if len(DTR_times) == max_laser_shots_number:
                    break

        return tuple(DTR_times)

    else:
        return False


if __name__ == "__main__":
    shtn: int = 43260
    times = get_DTRlaser_times(shtn)

    print(times)
