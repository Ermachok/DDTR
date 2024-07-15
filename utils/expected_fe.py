from calibrations.spectral_calibration.spectral_calibration import (get_filters_data,
                                                                    get_avalanche_data_phe,
                                                                    linear_interpolation,
                                                                    get_avalanche_data_amper)
import math
import json


def spect_dens_selden(temperature: float, wl_grid: list, theta_deg: float, lambda_0: float) -> list:
    # деление на lambda_0 - нормировка интеграла при переходе к нужной длине волны

    m_e = 9.1E-31
    c_light = 3E8
    q_elec = 1.6E-19

    alphaT = m_e * c_light * c_light / (2 * q_elec)
    theta = theta_deg * math.pi / 180.0
    alpha = alphaT / temperature
    section = []
    for wl in wl_grid:
        x = (wl / lambda_0) - 1
        a_loc = math.pow(1 + x, 3) * math.sqrt(2 * (1 - math.cos(theta)) * (1 + x) + math.pow(x, 2))
        b_loc = math.sqrt(1 + x * x / (2 * (1 - math.cos(theta)) * (1 + x))) - 1
        c_loc = math.sqrt(alpha / math.pi) * (1 - (15 / (16 * alpha)) + 345 / (512 * alpha * alpha))
        section.append((c_loc / a_loc) * math.exp(-2 * alpha * b_loc) / (lambda_0*1E-9)) # to meters
    return section


def f_e_calc(avalanche_Path, filter_Path):
    avalanche_wl, avalanche = get_avalanche_data_amper(avalanche_Path)
    filters_wl, filters_transm = get_filters_data(filter_Path, filters_transposed=True)

    wl_step = 0.2
    wl_grid = [700 + wl_step * step_count for step_count in range(1825)]
    Te_grid = [1 + 0.2 * step for step in range(5000)]

    avalanche_aw_interpolation = [linear_interpolation(wl, avalanche_wl, avalanche) for wl in wl_grid]
    filters_interpolation = []

    for filter in filters_transm:
        filters_interpolation.append([linear_interpolation(wl, filters_wl, filter) for wl in wl_grid])

    result = {'wl_grid': wl_grid,
              'Te_grid': Te_grid}

    for T in Te_grid:
        section = spect_dens_selden(T, wl_grid, 110, 1064.4)
        all_filters = []
        for filter in filters_interpolation:
            integral = 0
            for wl, sec, detector, filter_trans in zip(wl_grid, section, avalanche_aw_interpolation, filter):
                integral += sec * filter_trans * detector / (wl*1E-9)
            all_filters.append(integral * wl_step * 1E-9)
        result[T] = all_filters


    return result


if __name__ == '__main__':

    avalanche_Path = r'..\calibrations\calibration_datasheets\aw_hama.csv'
    filter_Path = r'..\calibrations\calibration_datasheets\filters_equator.csv'

    f_e = f_e_calc(avalanche_Path, filter_Path)

    with open('../config/f_expected_equator_june2024_v3.json', 'w') as f_file:
        json.dump(f_e, f_file, indent=4)

