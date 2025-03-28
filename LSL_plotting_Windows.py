import sys
from PyQt5.QtGui import QPalette, QColor, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from LSL_workers_Windows import EDAWorker, ACCWorker, DACWorker
from utilities import closest_division, colors, get_root_project_path, load_icon_path
import matplotlib
import os
import numpy as np
matplotlib.use('Qt5Agg')

class LSLPlotWindow(QMainWindow):
    def __init__(self, sample_rate, acc_enable, eda_enable, ld_mode):
        super().__init__()

        self.title_sz = 20
        self.xy_label_sz = 17
        self.tick_font_size = 14

        self.enable_eda = eda_enable
        self.enable_acc = acc_enable

        self.ld_mode = ld_mode

        # Set mode based on which signals are enabled
        if not self.enable_eda and self.enable_acc:
            self.mode = 0  # Only ACC enabled
        elif self.enable_eda and not self.enable_acc:
            self.mode = 1  # Only EDA enabled
        elif self.enable_eda and self.enable_acc:
            self.mode = 2  # Both EDA and ACC enabled

        self.setWindowTitle("Real-time Biosignal Viewer")
        self.setGeometry(100, 100, 2 * 800, 2 * 600)

        root_path = get_root_project_path()
        self.rsc_path = os.path.join(root_path, 'rsc')
        icon_path = load_icon_path(self.rsc_path, 'windows', self.ld_mode)
        self.setWindowIcon(QIcon(icon_path))

        # Layout and Canvas
        layout = QVBoxLayout()

        # Button for switching modes
        self.toggle_button = QPushButton("Switch to Dark Mode")
        self.toggle_button.clicked.connect(self.toggle_mode)
        self.toggle_button.setMinimumSize(200, 50)  # Width: 200, Height: 50
        layout.addWidget(self.toggle_button)

        self.figure = Figure()
        self.figure.subplots_adjust(hspace=0.5)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Initialize LSL stream
        self.inlet = None

        self.data_series = {'ACC': [], 'EDA': [], 'DAC': []}
        self.filtered_data = {'ACC': [], 'EDA': [], 'DAC': []}  # Stores filtered data
        self.moving_average_window = 5  # Use the last 10 samples to calculate the moving average

        target_vieweing_rate = 5  # 5 Hz

        self.vieweing_rate, self.vieweing_period, self.decimation_factor = closest_division(sample_rate,
                                                                                            target_vieweing_rate)

        self.vieweing_period = self.vieweing_period / 1000

        self.window_t_range = 15  # seconds

        self.max_data_points = self.vieweing_rate * self.window_t_range

        # Prepare axes list to hold only the necessary axes
        self.axs = {'ACC': None, 'EDA': None, 'DAC': None}
        self.lines = {'ACC': None, 'EDA': None, 'DAC': None}

        if self.mode == 0:
            plt_nums = [None, None, 111]

        elif self.mode == 1:
            plt_nums = [211, 212, None]

        elif self.mode == 2:
            plt_nums = [311, 312, 313]

        # Dynamically create subplots based on enabled signals
        if self.enable_eda:
            self.axs['EDA'] = self.figure.add_subplot(plt_nums[0])  # EDA at the top
            self.lines['EDA'], = self.axs['EDA'].plot([], [])
            self.axs['EDA'].set_title("EDA Signal", fontsize=self.title_sz)
            self.axs['EDA'].set_ylabel("Amplitude", fontsize=self.xy_label_sz)
            self.axs['EDA'].tick_params(axis='both', which='major', labelsize=self.tick_font_size)  # For major ticks

            self.axs['DAC'] = self.figure.add_subplot(plt_nums[1])  # DAC at the bottom
            self.lines['DAC'], = self.axs['DAC'].plot([], [])
            self.axs['DAC'].set_title("DAC Signal", fontsize=self.title_sz)
            self.axs['DAC'].set_ylabel("Amplitude", fontsize=self.xy_label_sz)
            self.axs['DAC'].tick_params(axis='both', which='major', labelsize=self.tick_font_size)  # For major ticks

            if not self.enable_acc:
                self.axs['DAC'].set_xlabel("Time [s]", fontsize=self.xy_label_sz)

        if self.enable_acc:
            self.axs['ACC'] = self.figure.add_subplot(plt_nums[2])  # DAC at the bottom
            self.lines['ACC'], = self.axs['ACC'].plot([], [])
            self.axs['ACC'].set_title("ACC Signal", fontsize=self.title_sz)
            self.axs['ACC'].set_ylabel("Amplitude", fontsize=self.xy_label_sz)
            self.axs['ACC'].set_xlabel("Time [s]", fontsize=self.xy_label_sz)
            self.axs['ACC'].tick_params(axis='both', which='major', labelsize=self.tick_font_size)  # For major ticks

        if self.ld_mode == 'Light':
            self.set_light_mode()
        else:
            self.set_dark_mode()

        if self.enable_eda:
            self.eda_worker = EDAWorker(sample_rate, mode=self.mode, window_size=20)
            self.dac_worker = DACWorker(sample_rate, mode=self.mode, window_size=None)

            self.eda_worker.signal.connect(self.plot_eda)  # Connect signal to update plot
            self.dac_worker.signal.connect(self.plot_dac)  # Connect signal to update plot

            self.eda_c = 0
            self.dac_c = 0

            self.eda_worker.start()  # Start the worker thread
            self.dac_worker.start()  # Start the worker thread

        if self.enable_acc:
            self.acc_worker = ACCWorker(sample_rate, mode=self.mode, window_size=5)
            self.acc_worker.signal.connect(self.plot_acc)  # Connect signal to update plot

            self.acc_c = 0

            self.acc_worker.start()  # Start the worker thread

        self.timer = QTimer()
        self.timer.timeout.connect(self.canvas.draw)  # Calls canvas.draw() at intervals
        self.timer.start(33)  # ~30 FPS (33 ms interval)
        self.elapsed_time = 0

    def plot_eda(self, new_data):

        type = 'EDA'

        if self.eda_c == 0:

            # filtered_data = self.apply_moving_average(type, new_data[0])

            self.data_series[type].append(new_data[0])

            if len(self.data_series[type]) > self.max_data_points:
                self.data_series[type] = self.data_series[type][-self.max_data_points:]
                sample_arr = np.array(range(self.elapsed_time - self.max_data_points, self.elapsed_time, 1))
                t_arr = sample_arr * self.vieweing_period

                self.lines[type].set_xdata(t_arr)

            else:
                sample_arr = np.array(range(len(self.data_series[type])))
                t_arr = sample_arr * self.vieweing_period
                self.lines[type].set_xdata(t_arr)

            self.lines[type].set_ydata(self.data_series[type])

            # Update plot limits and redraw
            self.axs[type].relim()
            self.axs[type].autoscale_view()

            self.elapsed_time += 1

        self.eda_c += 1
        self.eda_c = self.eda_c % self.decimation_factor

    def plot_dac(self, new_data):
        type = 'DAC'

        if self.dac_c == 0:

            self.data_series[type].append(new_data[0])

            if len(self.data_series[type]) > self.max_data_points:
                self.data_series[type] = self.data_series[type][-self.max_data_points:]
                sample_arr = np.array(range(self.elapsed_time - self.max_data_points, self.elapsed_time, 1))
                t_arr = sample_arr * self.vieweing_period

                self.lines[type].set_xdata(t_arr)

            else:
                sample_arr = np.array(range(len(self.data_series[type])))
                t_arr = sample_arr * self.vieweing_period
                self.lines[type].set_xdata(t_arr)

            self.lines[type].set_ydata(self.data_series[type])

            # Update plot limits and redraw
            self.axs[type].relim()
            self.axs[type].autoscale_view()

        self.dac_c += 1
        self.dac_c = self.dac_c % self.decimation_factor

    def plot_acc(self, new_data):
        type = 'ACC'

        if self.acc_c == 0:

            self.data_series[type].append(new_data[0])

            if len(self.data_series[type]) > self.max_data_points:
                self.data_series[type] = self.data_series[type][-self.max_data_points:]
                sample_arr = np.array(range(self.elapsed_time - self.max_data_points, self.elapsed_time, 1))
                t_arr = sample_arr * self.vieweing_period

                self.lines[type].set_xdata(t_arr)

            else:
                sample_arr = np.array(range(len(self.data_series[type])))
                t_arr = sample_arr * self.vieweing_period
                self.lines[type].set_xdata(t_arr)

            self.lines[type].set_ydata(self.data_series[type])

            # Update plot limits and redraw
            self.axs[type].relim()
            self.axs[type].autoscale_view()

        self.acc_c += 1
        self.acc_c = self.acc_c % self.decimation_factor

    def toggle_mode(self):
        if self.ld_mode == 'Light':
            self.set_dark_mode()
        else:
            self.set_light_mode()

        icon_path = load_icon_path(self.rsc_path, 'windows', self.ld_mode)
        self.setWindowIcon(QIcon(icon_path))

    def set_light_mode(self):
        self.ld_mode = 'Light'
        self.set_plot_colors(background='white', line_color=colors[self.ld_mode])
        self.toggle_button.setText("Switch to Dark Mode")
        self.toggle_button.setStyleSheet(
            f"background-color: {colors[self.ld_mode]['button']}; color: {colors[self.ld_mode]['text']}; border-radius: 15px;")
        QApplication.instance().setPalette(QApplication.style().standardPalette())

        # Define light mode color palette
        light_palette = QPalette()
        light_palette.setColor(QPalette.Window, QColor(255, 255, 255))  # White background for window
        light_palette.setColor(QPalette.WindowText, QColor(0, 0, 0))  # Black text
        light_palette.setColor(QPalette.Base, QColor(255, 255, 255))  # White background for text input areas
        light_palette.setColor(QPalette.AlternateBase, QColor(240, 240, 240))  # Light gray for alternate areas
        light_palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))  # White tooltips
        light_palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))  # Black text for tooltips
        light_palette.setColor(QPalette.Text, QColor(0, 0, 0))  # Black text
        light_palette.setColor(QPalette.Button, QColor(240, 240, 240))  # Light gray buttons
        light_palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))  # Black text on buttons
        light_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))  # Red color for bright text
        light_palette.setColor(QPalette.Link, QColor(42, 130, 218))  # Blue link color

        # Apply the light palette to the application
        QApplication.instance().setPalette(light_palette)

    def set_dark_mode(self):
        self.ld_mode = 'Dark'
        self.set_plot_colors(background='black', line_color=colors[self.ld_mode])
        self.toggle_button.setText("Switch to Light Mode")
        self.toggle_button.setStyleSheet(
            f"background-color: {colors[self.ld_mode]['button']}; color: {colors[self.ld_mode]['text']}; border-radius: 15px;")

        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Text, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))

        QApplication.instance().setPalette(dark_palette)

    def set_plot_colors(self, background, line_color):

        self.figure.patch.set_facecolor(background)
        self.canvas.draw()

        for ax in self.axs.values():
            if ax is not None:
                ax.set_facecolor(background)
                ax.spines['top'].set_color(line_color['axis'])
                ax.spines['right'].set_color(line_color['axis'])
                ax.spines['bottom'].set_color(line_color['axis'])
                ax.spines['left'].set_color(line_color['axis'])
                ax.xaxis.label.set_color(line_color['axis'])
                ax.yaxis.label.set_color(line_color['axis'])
                ax.tick_params(axis='both', colors=line_color['axis'])
                ax.title.set_color(line_color['text'])

        for var_name, line in self.lines.items():
            if line is not None:
                line.set_color(line_color['plots'][var_name])

    def closeEvent(self, event):
        # Clean up the timer when closing
        self.timer.stop()
        event.accept()

    def close_plot(self):
        """Handles cleanup and closes the plot window."""
        print("Closing LSL Plot Window...")
        # Add any additional cleanup logic here
        self.close()

def open_lsl_plot(sampling_rate, eda_enable, acc_enable, ld_mode):
    app = QApplication(sys.argv)
    window = LSLPlotWindow(sample_rate=sampling_rate, eda_enable=eda_enable, acc_enable=acc_enable, ld_mode=ld_mode)
    window.show()
    sys.exit(app.exec_())
