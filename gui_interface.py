import bisect
import tkinter as tk
from pathlib import Path
from tkinter import ttk

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from matplotlib.widgets import Slider, SpanSelector

from gui.plots import (draw_distance_from_separatrix, draw_expected,
                       draw_ir_camera, draw_phe, draw_raw_signals,
                       draw_separatrix)
from gui.utils_gui import (download_poly_data, get_divertor_data,
                           get_equator_data, get_ir_data, get_Xpoint)

initial_path_to_mcc = r"C:\TS_data\experimental_data\mcc_data"
initial_path_to_DTR_data = r"C:\TS_data\processed_shots"
initial_path_to_EQUATORTS_data = r"C:\TS_data\equator_TS_data"
initial_path_ir_camera = r"C:\TS_data\IR_data\Result_Temperature"


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("My App")
        self.geometry("1500x900")

        tabs = ttk.Notebook(self)

        tab1 = ControlTab(tabs)
        tabs.add(tab1, text="Control")

        tab2 = DTSPlotsTab(tabs)
        tabs.add(tab2, text="PLOTS")

        tab3 = RawSignalsTab(tabs)
        tabs.add(tab3, text="Raw signals")

        tabs.pack(expand=True, fill="both")


class ControlTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        label = ttk.Label(self, text="Tab 2")
        label.pack()


class RawSignalsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.poly_data = None
        self.shot_times = None

        self.data_loaded_flag = False
        self.shot_entry_changed = False

        self.input_frame = tk.Frame(self)
        self.input_frame.pack(side="top", pady=5, anchor="nw")

        self.discharge_num_entry = tk.Entry(self.input_frame, width=6)
        self.discharge_num_entry.pack(side="left", padx=5)

        self.load_button = tk.Button(
            self.input_frame, text="Download", command=self.load_data
        )
        self.load_button.pack(side="left", padx=5)

        self.indicator = tk.Label(self.input_frame, width=10, height=1, bg="red")
        self.indicator.pack(side="left")

        self.fibers_Label = tk.Label(self.input_frame, text="Choose fiber, Z =")
        self.fibers_Label.pack(side="left")

        self.box_combo_fibers = ttk.Combobox(
            self.input_frame, state="readonly", width=6
        )
        self.box_combo_fibers.pack(side="left")

        self.times_Label = tk.Label(self.input_frame, text="Choose timestamp")
        self.times_Label.pack(side="left")

        self.box_combo_times = ttk.Combobox(self.input_frame, state="readonly", width=8)
        self.box_combo_times.pack(side="left")

        self.plot_button = tk.Button(
            self.input_frame, text="Plot", command=self.draw_graphs
        )
        self.plot_button.pack(side="left")

        self.add_plot_button = tk.Button(
            self.input_frame,
            text="Add plot",
            command=lambda: self.draw_graphs(add_flag=True),
        )
        self.add_plot_button.pack(side="left")

        self.discharge_num_entry.bind("<Key>", self.entry_changed_handler)

        nrows, ncols = (4, 2)
        self.fig, self.axs = plt.subplots(nrows, ncols)
        self.fig.subplots_adjust(
            left=0.07, bottom=0.05, right=0.95, top=0.96, wspace=0.2, hspace=0.15
        )
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(
            side="top", fill="both", expand=True, padx=1, pady=1
        )

    def load_data(self):
        try:
            self.indicator.config(bg="green")

            discharge_num = self.discharge_num_entry.get()
            self.shot_times, self.poly_data = download_poly_data(discharge_num)

            self.box_combo_times["values"] = [time for time in self.shot_times]
            self.box_combo_fibers["values"] = [fiber.z_cm for fiber in self.poly_data]
            self.data_loaded_flag = True
        except Exception as er:
            print(f"Error occured while loading data {er}")

    def entry_changed_handler(self, event):
        self.shot_entry_changed = True
        self.indicator.config(bg="red")

    def draw_graphs(self, add_flag: bool = False):
        timestamp = self.box_combo_times.get()
        z_pos = self.box_combo_fibers.get()
        timestamp_ind = self.shot_times.index(float(timestamp))

        raw_data_plot = []
        phe_data = []
        for fiber in self.poly_data:
            if float(z_pos) == fiber.z_cm:
                for ch in range(fiber.ch_number):
                    raw_data_plot.append(
                        fiber.signals[ch][timestamp_ind + 1]
                    )  # +1 из-за записи дорожки для привязки к комбископу

                phe_data = fiber.get_signal_integrals()[0][timestamp_ind]
                fe_data = fiber.fe_data

        draw_raw_signals(
            z_pos, float(timestamp), raw_data_plot, self.axs, add_flag=add_flag
        )
        draw_phe(z_pos, float(timestamp), phe_data, self.axs[0][1], add_flag=add_flag)
        draw_expected(
            fe_data, self.axs[1][1], phe_data, float(timestamp), add_flag=add_flag
        )

        self.canvas.draw_idle()


class DTSPlotsTab(ttk.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.divertor_ts_data = {}
        self.equator_ts_data = {}
        self.ir_camera_data = {}

        self.input_shot_frame = tk.Frame(self)
        self.input_shot_frame.pack(side="top", pady=5, anchor="nw")

        self.path_label = tk.Label(self.input_shot_frame, text="PATH:")
        self.path_label.pack(side="left", padx=5)

        self.shot_num_entry = tk.Entry(self.input_shot_frame, width=10)
        self.shot_num_entry.pack(side="left", padx=5)

        self.button_update = tk.Button(
            self.input_shot_frame, text="Update", command=self.button_update_clicked
        )
        self.button_update.pack(side="left", padx=5)

        self.button_refresh = tk.Button(
            self.input_shot_frame, text="Refresh", command=self.button_refresh_clicked
        )
        self.button_refresh.pack(side="left", padx=5)

        self.mcc_label = tk.Label(self.input_shot_frame, text="MCC TIME:")
        self.mcc_label.pack(side="left", padx=5)

        self.mcc_entry = tk.Entry(self.input_shot_frame, width=10)
        self.mcc_entry.pack(side="left", padx=5)

        self.button_mcc = tk.Button(
            self.input_shot_frame, text="Get MCC", command=self.button_mcc_clicked
        )
        self.button_mcc.pack(side="left", padx=5)

        self.button_add_mcc = tk.Button(
            self.input_shot_frame, text="Add MCC", command=self.button_add_mcc_clicked
        )
        self.button_add_mcc.pack(side="left", padx=5)

        self.button_distance_separatrix = tk.Button(
            self.input_shot_frame,
            text="Distance to separatrix",
            command=self.button_distance_from_separatrix,
        )
        self.button_distance_separatrix.pack(side="left", padx=5)

        self.fig, self.axs = plt.subplots(2, 4)
        self.fig.subplots_adjust(
            left=0.07, bottom=0.05, right=0.95, top=0.96, wspace=0.2, hspace=0.15
        )
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(
            side="top", fill="both", expand=True, padx=1, pady=1
        )

        self.interactive = NavigationToolbar2Tk(self.canvas, self)
        self.interactive.update()
        self.interactive.pack(side="left", padx=5)

        pos = self.axs[1][3].get_position()
        slider_pos = [pos.x1 + 0.02, pos.y0 + 0.02, 0.01, pos.height - 0.02]

        self.ax_slider = plt.axes(slider_pos)
        self.slider = Slider(
            self.ax_slider,
            "Time, ms",
            100,
            220,
            orientation="vertical",
            valinit=100,
            valstep=1,
        )
        self.slider.on_changed(self.update_ir_graph)

        self.span_selectors = []
        for i in range(3):
            span = SpanSelector(
                self.axs[0][i],
                lambda xmin, xmax, idx=i: self.onselect(xmin, xmax, idx),
                direction="horizontal",
                useblit=True,
                props=dict(alpha=0.5, facecolor="red"),
            )
            self.span_selectors.append(span)

    def update_graphs(self, dtr_data):

        ne = dtr_data["ne(t)"]
        ne_err = dtr_data["ne_err(t)"]

        Te = dtr_data["Te(t)"]
        Te_err = dtr_data["Te_err(t)"]

        # trans
        Te_Z = np.array(Te).T
        ne_Z = np.array(ne).T

        Te_err_Z = np.array(Te_err).T
        ne_err_Z = np.array(ne_err).T

        times = dtr_data["t"]
        coord = dtr_data["Z"]

        for ax in self.axs.flat:
            ax.clear()
            ax.set_aspect("auto")

        for T, T_er, Z in zip(Te, Te_err, coord):
            self.axs[0][0].errorbar(
                times, T, yerr=T_er, fmt="-o", markersize=3, label=Z
            )

        for n, n_er, Z in zip(ne, ne_err, coord):
            self.axs[0][1].errorbar(
                times, n, yerr=n_er, fmt="-o", markersize=3, label=Z
            )

        for T, T_er, time in zip(Te_Z, Te_err_Z, times):
            self.axs[1][0].errorbar(
                coord, T, yerr=T_er, fmt="-o", markersize=3, label=str(time)
            )

        for n, n_er, time in zip(ne_Z, ne_err_Z, times):
            self.axs[1][1].errorbar(
                coord, n, yerr=n_er, fmt="-o", markersize=3, label=str(time)
            )

        for T, n, Z in zip(Te, ne, coord):
            self.axs[0][2].plot(
                times, [Te * ne for Te, ne in zip(T, n)], "-o", markersize=3, label=Z
            )

        for T, n, time in zip(Te_Z, ne_Z, times):
            self.axs[1][2].plot(
                coord,
                [Te * ne for Te, ne in zip(T, n)],
                "-o",
                markersize=3,
                label=str(time),
            )

        self.axs[0][0].set_ylabel("Te(t)")
        self.axs[0][0].set_ylim(0, 1000)

        self.axs[0][1].set_ylabel("ne(t)")
        self.axs[0][1].set_ylim(0, 1e20)

        self.axs[0][2].set_ylabel("ne * Te (t)")
        self.axs[0][2].set_ylim(0, 5e21)

        self.axs[1][0].set_ylabel("Te(Z)")
        self.axs[1][0].set_ylim(0, 1000)

        self.axs[1][1].set_ylabel("ne(Z)")
        self.axs[1][1].set_ylim(0, 1e20)

        self.axs[1][2].set_ylabel("ne * Te(Z)")
        self.axs[1][2].set_ylim(0, 1e21)

        for ax in self.axs[0]:
            ax.set_xlabel("time(ms)")
            ax.set_xlim(110, 240)

        for ax in self.axs[1]:
            ax.invert_xaxis()

        for ax in self.axs.flat:
            ax.grid()
            ax.legend()

        self.canvas.draw_idle()

    def button_update_clicked(self):
        shot_num = self.shot_num_entry.get()
        self.divertor_ts_data = get_divertor_data(shot_num)
        self.equator_ts_data = get_equator_data(shot_num)

        try:
            self.ir_camera_data = get_ir_data(shot_num)
            draw_ir_camera(shot_num, self.ir_camera_data, self.axs[1][3])

            self.update_graphs(self.divertor_ts_data)
        except FileNotFoundError:
            self.update_graphs(self.divertor_ts_data)
            self.axs[1][3].clear()
            self.ir_camera_data = {}
            print(f"No such files for IR camera")
        except Exception as e:
            self.update_graphs(self.divertor_ts_data)
            print(f"SOME EXCEPTION IN BUTTON UPDATE {e}")

    def button_refresh_clicked(self):
        if self.divertor_ts_data != {}:
            self.update_graphs(self.divertor_ts_data)
        else:
            self.button_update_clicked()

    def button_mcc_clicked(self):
        try:
            coord_divertor = self.divertor_ts_data["Z"]
            time = float(self.mcc_entry.get())
            shot_num = int(self.shot_num_entry.get())

            # equator_radia = get_equator_data(shot_num)['R']
            equator_radia = [0.6, 0.59, 0.57, 0.55, 0.52, 0.41]

            path_to_mcc: Path = Path(f"{initial_path_to_mcc}/mcc_{shot_num}.json")
            sep_data: dict = get_Xpoint(path_to_mcc, time)

            draw_separatrix(
                sep_data,
                time,
                shot_num,
                coord_divertor,
                equator_radia,
                ax=self.axs[0][3],
            )

            # print('R_body, Z_body, R_leg1, Z_leg1, R_leg2 Z_leg2')
            # for i in range(len(sep_data['body']['R'])):
            #     print(sep_data['body']['R'][i], sep_data['body']['Z'][i], end=' ')
            #     if i < len(sep_data['leg_1']['R']):
            #         print(sep_data['leg_1']['R'][i], sep_data['leg_1']['Z'][i], end=' ')
            #     else:
            #         print('- -', end=' ')
            #     if i < len(sep_data['leg_2']['R']):
            #         print(sep_data['leg_2']['R'][i], sep_data['leg_2']['Z'][i], end=' ')
            #     else:
            #         print('- -', end=' ')
            #     print()

            self.axs[0][3].figure.canvas.draw()

        except Exception as e:
            print(f"Some error {e}")

    def button_add_mcc_clicked(self):
        try:
            time = float(self.mcc_entry.get())
            shot_num = int(self.shot_num_entry.get())

            path_to_mcc = f"{initial_path_to_mcc}/mcc_{shot_num}.json"
            sep_data = get_Xpoint(path_to_mcc, time)

            draw_separatrix(sep_data, time, shot_num, add_flag=True, ax=self.axs[0][3])
            self.axs[0][3].figure.canvas.draw()
        except Exception as e:
            print(f"Some error {e}")

    def button_distance_from_separatrix(self):
        time = float(self.mcc_entry.get())
        shot_num = int(self.shot_num_entry.get())

        path_to_mcc = f"{initial_path_to_mcc}/mcc_{shot_num}.json"
        sep_data = get_Xpoint(path_to_mcc, time)

        draw_distance_from_separatrix(
            self.divertor_ts_data, self.equator_ts_data, sep_data, time
        )

    def update_plot_data(self, xmin, xmax, y_max, parameter):

        times = self.divertor_ts_data["t"]
        coord = self.divertor_ts_data["Z"]

        if parameter == "Te":
            Te = self.divertor_ts_data["Te(t)"]
            Te_err = self.divertor_ts_data["Te_err(t)"]
            Te_Z = np.array(Te).T
            Te_err_Z = np.array(Te_err).T

            self.axs[1][0].clear()

            for T, T_er, time in zip(Te_Z, Te_err_Z, times):
                if xmin < time < xmax:
                    self.axs[1][0].errorbar(
                        coord, T, yerr=T_er, fmt="-o", markersize=3, label=str(time)
                    )

            self.axs[1][0].set_ylim(0, y_max)

            self.axs[1][0].set_ylabel("T(Z)")
            self.axs[1][0].set_xlabel("Z(cm)")
            self.axs[1][0].legend()
            self.axs[1][0].grid()
            self.axs[1][0].invert_xaxis()
            self.axs[1][0].figure.canvas.draw_idle()

        elif parameter == "ne":
            ne = self.divertor_ts_data["ne(t)"]
            ne_err = self.divertor_ts_data["ne_err(t)"]
            ne_Z = np.array(ne).T
            ne_err_Z = np.array(ne_err).T
            self.axs[1][1].clear()

            for n, n_er, time in zip(ne_Z, ne_err_Z, times):
                if xmin < time < xmax:
                    self.axs[1][1].errorbar(
                        coord, n, yerr=n_er, fmt="-o", markersize=3, label=str(time)
                    )

            self.axs[1][1].set_ylim(0, y_max)
            self.axs[1][1].set_ylabel("n(Z)")
            self.axs[1][1].set_xlabel("Z(cm)")
            self.axs[1][1].legend()
            self.axs[1][1].grid()
            self.axs[1][1].invert_xaxis()
            self.axs[1][1].figure.canvas.draw_idle()

        elif parameter == "pe":
            ne = self.divertor_ts_data["ne(t)"]
            Te = self.divertor_ts_data["Te(t)"]
            ne_Z = np.array(ne).T
            Te_Z = np.array(Te).T

            self.axs[1][2].clear()

            for T, n, time in zip(Te_Z, ne_Z, times):
                if xmin < time < xmax:
                    self.axs[1][2].plot(
                        coord,
                        [Te * ne for Te, ne in zip(T, n)],
                        "-o",
                        markersize=3,
                        label=str(time),
                    )

            self.axs[1][2].set_ylim(0, y_max)

            self.axs[1][2].set_ylabel("ne * Te (Z)")
            self.axs[1][2].set_xlabel("Z(cm)")
            self.axs[1][2].legend()
            self.axs[1][2].grid()
            self.axs[1][2].invert_xaxis()
            self.axs[1][2].figure.canvas.draw_idle()

    def onselect(self, xmin, xmax, idx):
        elems = self.axs[0][idx].get_children()
        all_y = []
        x_data = None

        for element in elems:
            if isinstance(element, plt.Line2D):
                if x_data is None:
                    x_data = element.get_xdata()
                all_y.append(element.get_ydata())

        all_y = np.array(all_y)
        all_x = np.array(x_data)

        left_index = np.searchsorted(all_x, xmin, side="left")
        right_index = np.searchsorted(all_x, xmax, side="right") - 1

        y_values = all_y[:, left_index : right_index + 1]
        y_value_max = np.max(y_values)

        ax = self.axs[0][idx]
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(0, y_value_max * 1.2)

        ax.figure.canvas.draw_idle()

        self.update_plot_data(
            xmin,
            xmax,
            y_value_max * 1.2,
            "Te" if idx == 0 else "ne" if idx == 1 else "pe",
        )

    def update_ir_graph(self, val):

        self.axs[1][3].clear()

        ir_data = self.ir_camera_data
        time = self.slider.val
        ir_camera_time_ind = bisect.bisect_left(ir_data["times_ms"], time)
        ir_camera_time = ir_data["times_ms"][ir_camera_time_ind]

        self.axs[1][3].plot(ir_data["radii"], ir_data[ir_camera_time])

        self.axs[1][3].set_ylim(0, 140)
        self.axs[1][3].figure.canvas.draw_idle()


if __name__ == "__main__":
    app = App()
    app.mainloop()
