import bisect
import math
import os
import statistics

from calibrations.spectral_calibration.spectral_calibration import (
    get_avalanche_data_amper, get_avalanche_data_phe, get_filters_data)
from utils.POLY_v2 import Polychromator


def linear_interpolation(x_point: float, Xdata: list, Ydata: list) -> float:
    """

    :param x_point: точка в которой надо найти
    :param Xdata: лист по Х данных
    :param Ydata: лист по Н данных
    :return: линейная интерполяция
    """
    ind_1 = bisect.bisect_right(Xdata, x_point) - 1
    ind_2 = bisect.bisect_right(Xdata, x_point)

    if Xdata[ind_1] > x_point > Xdata[ind_2]:
        raise Exception
    else:
        y_point = Ydata[ind_1] + (Ydata[ind_2] - Ydata[ind_1]) / (
            Xdata[ind_2] - Xdata[ind_1]
        ) * (x_point - Xdata[ind_1])
        # print(Xdata[ind_1], Ydata[ind_1], Xdata[ind_2], Ydata[ind_2], x_point, y_point)
        return y_point


def get_raman_wl_section(
    gas_temperature: float, las_wl: float = 1064.4e-9, J_lim: int = 50
) -> tuple[list, list]:
    k_bolt = 1.38e-23  # J/K

    gamma_squared = 0.51e-60  # m^6
    B_0 = 198.96  # m^-1
    h_plank = 6.63e-34
    c_light = 3e8
    exp = 2.718

    exp_coef = h_plank * c_light * B_0 / (k_bolt * gas_temperature)

    def calculate_normalizing_coef(J_lim):
        A = 0
        for j in range(0, J_lim):
            if j % 2 == 0:
                A += 3 * (2 * j + 1) * exp ** (-exp_coef * j * (j + 1))
            else:
                A += 6 * (2 * j + 1) * exp ** (-exp_coef * j * (j + 1))
        return A

    def population(J, A):
        if J % 2 == 0:
            F = A ** (-1) * 6 * (2 * J + 1) * exp ** (-exp_coef * J * (J + 1))
        else:
            F = A ** (-1) * 3 * (2 * J + 1) * exp ** (-exp_coef * J * (J + 1))
        return F

    A = calculate_normalizing_coef(J_lim)

    raman_wl_list = []
    raman_section_list = []
    const = gamma_squared * 64 * math.pi**4 / 45
    for J in range(2, J_lim):
        wl_scat = 1 / ((1 / las_wl) + B_0 * (4 * J - 2))
        ram_sec = const * 3 * J * (J - 1) / (2 * (2 * J + 1) * (2 * J - 1) * wl_scat**4)
        raman_wl_list.append(wl_scat * 1e9)
        raman_section_list.append(ram_sec * population(J, A))
    return raman_wl_list, raman_section_list


def get_calibration_integrals(poly: Polychromator, t_step: float = 0.325) -> list:
    all_const = poly.gain.resulting_multiplier
    all_shots_signal = []
    for shot in range(0, len(poly.signals[0])):

        for poly_ch in range(1):
            signal_indices = [
                bisect.bisect_left(
                    poly.signals_time[shot], poly.config[poly_ch]["sig_LeftBord"]
                ),
                bisect.bisect_right(
                    poly.signals_time[shot], poly.config[poly_ch]["sig_RightBord"]
                ),
            ]

            signal_integral = (
                sum(poly.signals[poly_ch][shot][signal_indices[0] : signal_indices[1]])
                * t_step
            )
            all_shots_signal.append(signal_integral * all_const)

    return all_shots_signal


def get_ophir_data(ophir_path: str, ophir_shot_name) -> list:
    for file in os.listdir(ophir_path):
        if file.endswith(ophir_shot_name):
            with open(rf"{ophir_path}\{file}", "r") as ophir_file:
                ophir_data = ophir_file.readlines()

            ophir_energy = [
                float(ophir_data[36 + i].split("\t")[1])
                for i in range(len(ophir_data) - 36)
            ]
            return ophir_energy

    print("No such ophir file")
    raise FileExistsError


def phe_to_laser(poly: Polychromator, laser_ophir: list):
    ophir_to_J = 0.0275

    integrals_phe = get_calibration_integrals(poly)

    if len(integrals_phe) == len(laser_ophir):
        phe_to_laser = [
            phe / (laser / ophir_to_J) for phe, laser in zip(integrals_phe, laser_ophir)
        ]
    else:
        print("Different amount of shots")
        raise IndexError

    return phe_to_laser


def calculate_calibration_coef(
    fibers: list[Polychromator],
    ophir_data_path: str,
    ophir_shot_name,
    p_torr: float,
    gas_temperature: float,
):

    avalanche_Path = r"C:\Users\NE\PycharmProjects\DDTS\calibrations\calibration_datasheets\aw_hama.csv"

    k_bolt = 1.38e-23  # J/K
    gas_temperature = gas_temperature + 273.15  # K
    p_pascal = p_torr * 133.3  # pascal
    n = p_pascal / (k_bolt * gas_temperature)
    h_plank = 6.626e-34
    c_speed = 3e8
    laser_wl = 1064.4e-9
    polarization_coef = 1.75

    photon_energy = h_plank * c_speed / laser_wl

    avalanche_wl, avalanche_phe = get_avalanche_data_phe(avalanche_Path)

    raman_wl, raman_section = get_raman_wl_section(
        gas_temperature=gas_temperature, las_wl=1064.4e-9
    )

    laser_ophir_data = get_ophir_data(ophir_data_path, ophir_shot_name)

    result_absolut = {}
    for fiber in fibers:
        calib_phe_to_laser = phe_to_laser(fiber, laser_ophir_data)

        if "T5" in fiber.poly_name:
            filter_Path = r"C:\Users\NE\PycharmProjects\DDTS\calibrations\calibration_datasheets\t15_filters_model.csv"
        else:
            filter_Path = r"C:\Users\NE\PycharmProjects\DDTS\calibrations\calibration_datasheets\filters_equator.csv"

        filters_wl, filters_transm = get_filters_data(
            filter_Path, filters_transposed=True
        )
        integral = 0
        for ram_wl, ram_sec in zip(raman_wl, raman_section):
            filter = linear_interpolation(ram_wl, filters_wl, filters_transm[0])
            detector = linear_interpolation(ram_wl, avalanche_wl, avalanche_phe)

            integral += ram_sec * filter * detector

        calibration_result = (
            statistics.median(calib_phe_to_laser)
            * photon_energy
            / (integral * polarization_coef * n)
        )
        result_absolut[fiber.poly_name] = calibration_result

    return result_absolut
