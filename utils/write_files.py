import os
from itertools import zip_longest
from pathlib import Path

from utils.POLY_v2 import Polychromator


def write_results(
        discharge_num: str, path, laser_shots_times: list, fibers: list[Polychromator]
):
    try:
        path_to_write = os.path.join(path, discharge_num)
        os.mkdir(path_to_write)
        laser_shots_times = [str(num) for num in laser_shots_times]

        with open(rf"{path_to_write}\{discharge_num}_Te.csv", "w") as temperature_file:
            from_shot = 3
            to_shot = 20
            temperature_file.write(
                "Z(cm), "
                + ", error, ".join(laser_shots_times[from_shot:to_shot])
                + ", error\n"
            )
            for fiber in fibers:
                result_string = [
                    f"{t_e}, {te_err}"
                    for t_e, te_err in zip(
                        fiber.temperatures[from_shot:to_shot],
                        fiber.errors_T[from_shot:to_shot],
                    )
                ]
                temperature_file.write(
                    f"{str(fiber.z_cm)}, " + ", ".join(result_string) + "\n"
                )

        with open(rf"{path_to_write}\{discharge_num}_ne.csv", "w") as density_file:
            from_shot = 3
            to_shot = 20
            density_file.write(
                "Z(cm), "
                + ", error, ".join(laser_shots_times[from_shot:to_shot])
                + ", error\n"
            )
            for fiber in fibers:
                result_string = [
                    f"{n_e}, {ne_err}"
                    for n_e, ne_err in zip(
                        fiber.density[from_shot:to_shot],
                        fiber.errors_n[from_shot:to_shot],
                    )
                ]
                density_file.write(
                    f"{str(fiber.z_cm)}, " + ", ".join(result_string) + "\n"
                )

    except Exception as e:
        print(f"Error in write_results: {e}")
        pass


def write_separatrix(
        filepath: Path, sht_num: int, timestamp: float, sep_data: dict
) -> None:
    filename = Path(f"{filepath}/mcc_{sht_num}_{timestamp}.csv")

    if filename.is_file():
        print("File already exist!")
        pass

    with open(filename, "w") as file:
        file.write("body_R, body_Z, leg_1_R, leg_1_Z, leg_2_R, leg_2_Z\n")
        for body_R, body_Z, leg_1_R, leg_1_Z, leg_2_R, leg_2_Z in zip_longest(
                sep_data["body"]["R"],
                sep_data["body"]["Z"],
                sep_data["leg_1"]["R"],
                sep_data["leg_1"]["Z"],
                sep_data["leg_2"]["R"],
                sep_data["leg_2"]["Z"],
        ):
            formatted_row = (
                f"{body_R}, {body_Z}, {leg_1_R}, {leg_1_Z}, {leg_2_R}, {leg_2_Z},"
            )
            file.write(formatted_row + "\n")

    return


def write_distance(filepath: Path, timestamp: float,
                   equator_distances, ne_equator, ne_equator_err, te_equator, te_equator_err,
                   dts_distances, ne_dts, ne_dts_err, te_dts, te_dts_err) -> None:
    filename = Path(f"mcc_{timestamp}.csv")

    if filename.is_file():
        print("File already exist!")
        pass

    with open(filename, "w") as file:
        file.write(
            'eq_dist, ne_eq, ne_err, te_eq, te_err, dts_dist, ne_dts, ne_err, te_dts, te_err' + '\n')
        for eq_dist, ne_eq, ne_eq_err, te_eq, te_eq_err, d_dist, ne_d, ne_d_err, te_d, te_d_err in zip_longest(
                equator_distances, ne_equator, ne_equator_err, te_equator, te_equator_err,
                dts_distances, ne_dts, ne_dts_err, te_dts, te_dts_err):
            formatted_row = (
                f"{eq_dist}, {ne_eq}, {ne_eq_err}, {te_eq}, {te_eq_err},"
                f" {d_dist}, {ne_d}, {ne_d_err}, {te_d}, {te_d_err}"
            )
            file.write(formatted_row + "\n")
