import bisect
import math

from calibrations.spectral_calibration.spectral_calibration import (
    get_avalanche_data_phe, get_filters_data)


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
        print("Interpolation exception")
        raise Exception

    else:
        y_point = Ydata[ind_1] + (Ydata[ind_2] - Ydata[ind_1]) / (
            Xdata[ind_2] - Xdata[ind_1]
        ) * (x_point - Xdata[ind_1])
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


def calib_coef_cross_validation(
    p_torr: float, gas_temperature: float, n_phe=2, laser_energy=1.5
):
    """

    :param laser_energy:
    :param n_phe:
    :param p_torr:
    :param gas_temperature: Celsius!
    :return:
    """
    avalanche_Path = r"..\calibrations\calibration_datasheets\aw_hama.csv"
    filter_Path = r"..\calibrations\calibration_datasheets\filters_equator.csv"

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
    filters_wl, filters_transm = get_filters_data(filter_Path, filters_transposed=True)
    raman_wl, raman_section = get_raman_wl_section(
        gas_temperature=gas_temperature, las_wl=laser_wl
    )

    first_filter = filters_transm[0]

    integral = 0
    for ram_wl, ram_sec in zip(raman_wl, raman_section):
        filter = linear_interpolation(ram_wl, filters_wl, first_filter)
        detector = linear_interpolation(ram_wl, avalanche_wl, avalanche_phe)

        integral += ram_sec * filter * detector

    calibration_result = (
        n_phe * photon_energy / (integral * polarization_coef * n * laser_energy)
    )

    return {
        "n": n,
        "raman": (raman_wl, raman_section),
        "integral": integral,
        "calibration_result": calibration_result,
    }


if __name__ == "__main__":
    ans = calib_coef_cross_validation(
        p_torr=100, gas_temperature=20, n_phe=2, laser_energy=1.5
    )

    ram_wl, ram_sec = ans["raman"]
    print(ans["calibration_result"])
