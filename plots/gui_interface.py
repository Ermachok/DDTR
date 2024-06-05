import os
import tkinter as tk
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.widgets import SpanSelector

from utils import get_Xpoint, draw_separatrix

initial_path_to_mcc = r'C:\Users\NE\Desktop\DTR_data\mcc_data'
initial_path_to_DTR_data = r'C:\Users\NE\Desktop\DTR_data\TS_data'
initial_eq_data = 'None'


class DTSPlots:
    def __init__(self, root):

        self.sht_data = {}

        self.root = root
        self.root.geometry("1200x1000")
        self.root.title("DTS PLOTS")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="Tab 1")

        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text="PLOTS")

        self.input_frame = tk.Frame(self.tab2)
        self.input_frame.pack(side="top", pady=5, anchor='nw')

        self.path_label = tk.Label(self.input_frame, text="PATH:")
        self.path_label.pack(side="left", padx=5)

        self.shot_num_entry = tk.Entry(self.input_frame, width=10)
        self.shot_num_entry.pack(side="left", padx=5)

        self.button_update = tk.Button(self.input_frame, text="Update", command=self.button_update_clicked)
        self.button_update.pack(side="left", padx=5)

        self.button_refresh = tk.Button(self.input_frame, text="Refresh", command=self.button_refresh_clicked)
        self.button_refresh.pack(side="left", padx=5)

        self.mcc_label = tk.Label(self.input_frame, text="MCC TIME:")
        self.mcc_label.pack(side="left", padx=5)

        self.mcc_entry = tk.Entry(self.input_frame, width=10)
        self.mcc_entry.pack(side="left", padx=5)

        self.button_mcc = tk.Button(self.input_frame, text="Get MCC", command=self.button_mcc_clicked)
        self.button_mcc.pack(side="left", padx=5)

        self.button_add_mcc = tk.Button(self.input_frame, text="Add MCC", command=self.button_add_mcc_clicked)
        self.button_add_mcc.pack(side="left", padx=5)

        self.fig, self.axs = plt.subplots(2, 3)
        self.fig.subplots_adjust(left=0.07, bottom=0.05, right=0.95, top=0.96, wspace=0.2, hspace=0.15)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.tab2)
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True, padx=1, pady=1)

        self.interactive = NavigationToolbar2Tk(self.canvas, window=self.input_frame)
        self.interactive.update()
        self.interactive.pack(side="left", padx=5)

        self.span_selectors = []
        self.span_02_flag = True
        for i in range(3):
            span = SpanSelector(self.axs[0][i], lambda xmin, xmax, idx=i: self.onselect(xmin, xmax, idx),
                                direction='horizontal', useblit=True, props=dict(alpha=0.5, facecolor='red'))
            self.span_selectors.append(span)

    def update_graphs(self, data):
        self.span_02_flag = True

        ne = data['ne(t)']
        ne_err = data['ne_err(t)']

        Te = data['Te(t)']
        Te_err = data['Te_err(t)']

        # trans
        Te_Z = list(map(list, zip(*Te)))
        ne_Z = list(map(list, zip(*ne)))

        Te_err_Z = list(map(list, zip(*Te_err)))
        ne_err_Z = list(map(list, zip(*ne_err)))

        times = data['t']
        coord = data['Z']

        for ax in self.axs.flat:
            ax.clear()
            ax.set_aspect('auto')

        for T, T_er, Z in zip(Te, Te_err, coord):
            self.axs[0][0].errorbar(times, T, yerr=T_er, fmt='-o', markersize=3, label=Z)

        for n, n_er, Z in zip(ne, ne_err, coord):
            self.axs[0][1].errorbar(times, n, yerr=n_er, fmt='-o', markersize=3, label=Z)

        for T, T_er, time in zip(Te_Z, Te_err_Z, times):
            self.axs[1][0].errorbar(coord, T, yerr=T_er, fmt='-o', markersize=3, label=str(time))

        for n, n_er, time in zip(ne_Z, ne_err_Z, times):
            self.axs[1][1].errorbar(coord, n, yerr=n_er, fmt='-o', markersize=3, label=str(time))

        for T, n, Z in zip(Te, ne, coord):
            self.axs[0][2].plot(times, [Te * ne for Te, ne in zip(T, n)], '-o', markersize=3, label=Z)

        for T, n, time in zip(Te_Z, ne_Z, times):
            self.axs[1][2].plot(coord, [Te * ne for Te, ne in zip(T, n)], '-o', markersize=3, label=str(time))

        for ax in self.axs[0]:
            ax.set_xlabel('time(ms)')

        for ax in self.axs[0]:
            ax.set_xlabel('time(ms)')

        for ax in self.axs[1]:
            ax.set_xlim(100, 240)
            ax.invert_xaxis()

        for ax in self.axs.flat:
            ax.grid()
            ax.legend()

        self.axs[0][0].set_ylabel('Te(t)')
        self.axs[0][0].set_ylim(0, 1500)

        self.axs[0][1].set_ylabel('ne(t)')
        self.axs[0][1].set_ylim(0, 1e20)

        self.axs[0][2].set_ylabel('ne * Te (t)')
        self.axs[0][2].set_ylim(0, 5e21)

        self.axs[1][0].set_ylabel('Te(Z)')
        self.axs[1][0].set_ylim(0, 1500)

        self.axs[1][1].set_ylabel('ne(Z)')
        self.axs[1][1].set_ylim(0, 1e20)

        self.axs[1][2].set_ylabel('ne * Te(Z)')
        self.axs[1][2].set_ylim(0, 1e21)

        self.canvas.draw()


    def get_divertor_data(self, shot_number):
        path = fr'{initial_path_to_DTR_data}\%d' % int(shot_number)
        files = os.listdir(path)
        coordinate = []

        for file_name in files:
            if 'ne' in file_name:
                ne_all = []
                ne_err_all = []
                with open(path + fr'\{file_name}') as ne_file:
                    ne_file_data = ne_file.readlines()

                for ind, line in enumerate(ne_file_data):
                    ne = []
                    ne_err = []
                    if ind == 0:
                        times = [float(t) for t in line.split(',')[1::2]]
                    if ind > 0:
                        line_data_list = line.split(', ')
                        coordinate.append(line_data_list[0])
                        ne = [float(n) for n in line_data_list[1::2]]
                        ne_err = [float(n_err) for n_err in line_data_list[2::2]]

                        ne_all.append(ne)
                        ne_err_all.append(ne_err)

            elif 'Te' in file_name:
                Te_all = []
                Te_err_all = []
                with open(path + fr'\{file_name}') as te_file:
                    te_file_data = te_file.readlines()

                for ind, line in enumerate(te_file_data):
                    te = []
                    te_err = []
                    if ind > 0:
                        line_data_list = line.split(', ')
                        te = [float(t) for t in line_data_list[1::2]]
                        te_err = [float(t_err) for t_err in line_data_list[2::2]]

                        Te_all.append(te)
                        Te_err_all.append(te_err)

        return {'discharge': shot_number, 't': times, 'Z': coordinate,
                'ne(t)': ne_all, 'ne_err(t)': ne_err_all,
                'Te(t)': Te_all, 'Te_err(t)': Te_err_all}

    def get_equator_data(self, path):
        path = fr'{initial_eq_data}\%d' % int(path)
        files = os.listdir(path)
        coordinate = []

        for file in files:
            if 'n(R)' in file:
                with open(path + fr'\{file}') as ne_file:
                    ne_file_data = ne_file.readlines()

                for ind, line in enumerate(ne_file_data):
                    if ind > 1:
                        line_data_list = line.split(', ')
                        coordinate.append(float(line_data_list[0]) / 1000)
                return {'R': coordinate}

    def button_update_clicked(self):
        shot_num = self.shot_num_entry.get()
        self.sht_data = self.get_divertor_data(shot_num)
        self.update_graphs(self.sht_data)

    def button_refresh_clicked(self):
        self.span_02_flag = True
        if self.sht_data != {}:
            self.update_graphs(self.sht_data)
        else:
            self.button_update_clicked()

    def button_mcc_clicked(self):
        try:
            self.span_02_flag = False
            coord_divertor = self.sht_data['Z']
            time = float(self.mcc_entry.get())
            shot_num = int(self.shot_num_entry.get())

            # equator_radia = self.get_equator_data(shot_num)['R']
            equator_radia = [0.6, 0.59, 0.57, 0.55, 0.52, 0.41]

            path_to_mcc = f'{initial_path_to_mcc}/mcc_{shot_num}.json'
            sep_data = get_Xpoint(path_to_mcc, time)

            draw_separatrix(sep_data, time, shot_num, coord_divertor, equator_radia, ax=self.axs[0][2])
            self.axs[0][2].figure.canvas.draw()

        except Exception as e:
            print(f'Some error {e}')

    def button_add_mcc_clicked(self):
        try:
            self.span_02_flag = False
            time = float(self.mcc_entry.get())
            shot_num = int(self.shot_num_entry.get())

            path_to_mcc = f'{initial_path_to_mcc}/mcc_{shot_num}.json'
            sep_data = get_Xpoint(path_to_mcc, time)

            draw_separatrix(sep_data, time, shot_num, add_flag=True, ax=self.axs[0][2])
            self.axs[0][2].figure.canvas.draw()
        except Exception as e:
            print(f'Some error {e}')

    def update_plot_data(self, xmin, xmax, y_max, parameter):

        times = self.sht_data['t']
        coord = self.sht_data['Z']

        if parameter == 'Te':
            Te = self.sht_data['Te(t)']
            Te_err = self.sht_data['Te_err(t)']

            Te_Z = np.array(Te).T
            Te_err_Z = np.array(Te_err).T

            # Te_Z = list(map(list, zip(*Te)))
            # Te_err_Z = list(map(list, zip(*Te_err)))

            self.axs[1][0].clear()

            for T, T_er, time in zip(Te_Z, Te_err_Z, times):
                if xmin < time < xmax:
                    self.axs[1][0].errorbar(coord, T, yerr=T_er, fmt='-o', markersize=3, label=str(time))

            self.axs[1][0].set_ylim(0, y_max)

            self.axs[1][0].set_ylabel('T(Z)')
            self.axs[1][0].set_xlabel('Z(cm)')
            self.axs[1][0].legend()
            self.axs[1][0].grid()
            self.axs[1][0].invert_xaxis()
            self.axs[1][0].figure.canvas.draw()

        elif parameter == 'ne':
            ne = self.sht_data['ne(t)']
            ne_err = self.sht_data['ne_err(t)']

            ne_Z = np.array(ne).T
            ne_err_Z = np.array(ne_err).T

            self.axs[1][1].clear()

            for n, n_er, time in zip(ne_Z, ne_err_Z, times):
                if xmin < time < xmax:
                    self.axs[1][1].errorbar(coord, n, yerr=n_er, fmt='-o', markersize=3, label=str(time))

            self.axs[1][1].set_ylim(0, y_max)

            self.axs[1][1].set_ylabel('n(Z)')
            self.axs[1][1].set_xlabel('Z(cm)')
            self.axs[1][1].legend()
            self.axs[1][1].grid()
            self.axs[1][1].invert_xaxis()
            self.axs[1][1].figure.canvas.draw()

        elif parameter == 'pe':
            if not self.span_02_flag:
                return

            ne = self.sht_data['ne(t)']
            Te = self.sht_data['Te(t)']

            ne_Z = np.array(ne).T
            Te_Z = np.array(Te).T

            self.axs[1][2].clear()

            for T, n, time in zip(Te_Z, ne_Z, times):
                if xmin < time < xmax:
                    self.axs[1][2].plot(coord, [Te * ne for Te, ne in zip(T, n)], '-o', markersize=3, label=str(time))

            self.axs[1][2].set_ylim(0, y_max)

            self.axs[1][2].set_ylabel('ne * Te (Z)')
            self.axs[1][2].set_xlabel('Z(cm)')
            self.axs[1][2].legend()
            self.axs[1][2].grid()
            self.axs[1][2].invert_xaxis()
            self.axs[1][2].figure.canvas.draw()

    def onselect(self, xmin, xmax, idx):
        elems = self.axs[0][idx].get_children()

        if idx == 2 and not self.span_02_flag:
            return

        all_y = []
        x_data = []
        for element in elems:
            if isinstance(element, mpl.lines.Line2D):
                if len(x_data) == 0:
                    x_data = element.get_xdata()
                y_data = element.get_ydata()
                all_y.append(list(y_data))

        all_x = np.array(x_data)

        left_index = np.abs(all_x - xmin).argmin()
        right_index = np.abs(all_x - xmax).argmin()

        y_value_max = max([max(y_coord[left_index:right_index + 1]) for y_coord in all_y])

        self.axs[0][idx].set_xlim(xmin, xmax)
        self.axs[0][idx].set_ylim(0, y_value_max * 1.2)
        self.axs[0][idx].figure.canvas.draw()

        self.update_plot_data(xmin, xmax, y_value_max * 1.2, 'Te' if idx == 0 else 'ne' if idx == 1 else 'pe')


if __name__ == '__main__':
    root = tk.Tk()
    app = DTSPlots(root)
    root.mainloop()
