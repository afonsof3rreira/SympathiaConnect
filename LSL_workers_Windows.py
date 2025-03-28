from PyQt5.QtCore import QThread, pyqtSignal
from pylsl import StreamInlet, resolve_stream
import time


class ACCWorker(QThread):
    signal = pyqtSignal(list)  # Signal to pass new data to the main GUI thread

    def __init__(self, sample_rate, mode=None, window_size=None, parent=None):
        super().__init__(parent)
        self.sample_rate = sample_rate
        self.running = True

        self.window_size = window_size  # Number of samples for the moving average

        self.ma_buffer = []  # Unified buffer name for moving average

        # mode == 0 > ACC only (we select the first signal, ACC X)
        # mode == 1 > EDA and DAC only
        # mode == 2 > ALL (in this case, since EDA and DAC are first in the table, the index is 2)

        if mode == 0:
            self.index = 0
        if mode == 2:
            self.index = 2

    def init_lsl_stream(self):
        streams = resolve_stream()
        self.inlet = StreamInlet(streams[0])

    def run(self):
        self.init_lsl_stream()

        while self.running:
            sample, _ = self.inlet.pull_sample(timeout=0.01)

            if sample:

                if self.window_size is not None:
                    # Append the current sample to the buffer
                    self.ma_buffer.append(sample[self.index])

                    # If the buffer exceeds the window size, remove the oldest sample
                    if len(self.ma_buffer) > self.window_size:
                        self.ma_buffer.pop(0)

                    # Calculate the moving average and emit the data
                    avg_sample = sum(self.ma_buffer) / len(self.ma_buffer)
                    self.signal.emit([avg_sample])
                else:
                    self.signal.emit([sample[0]])

            time.sleep(0.5 / (self.sample_rate))  # Adjust to the desired sample rate

    def stop(self):
        self.running = False
        self.quit()
        self.wait()  # Wait for the thread to finish

class EDAWorker(QThread):
    signal = pyqtSignal(list)  # Signal to pass new data to the main GUI thread

    def __init__(self, sample_rate, mode, window_size=None, parent=None):
        super().__init__(parent)
        self.sample_rate = sample_rate
        self.running = True

        # mode == 0 > ACC only
        # mode == 1 > EDA and DAC only (always index 0)
        # mode == 2 > ALL (always index 0)

        self.index = 0

        self.window_size = window_size  # Number of samples for the moving average

        self.ma_buffer = []  # Unified buffer name for moving average

    def init_lsl_stream(self):
        streams = resolve_stream()
        self.inlet = StreamInlet(streams[0])

    def run(self):
        self.init_lsl_stream()

        while self.running:
            sample, _ = self.inlet.pull_sample(timeout=0.01)

            if sample:

                if self.window_size is not None:

                    # Append the current sample to the buffer

                    self.ma_buffer.append(sample[self.index])

                    # If the buffer exceeds the window size, remove the oldest sample
                    if len(self.ma_buffer) > self.window_size:
                        self.ma_buffer.pop(0)

                    # Calculate the moving average and emit the data
                    avg_sample = sum(self.ma_buffer) / len(self.ma_buffer)
                    self.signal.emit([avg_sample])
                else:
                    self.signal.emit([sample[self.index]])

            time.sleep(0.5 / (self.sample_rate))  # Adjust to the desired sample rate

    def stop(self):
        self.running = False
        self.quit()
        self.wait()  # Wait for the thread to finish


class DACWorker(QThread):
    signal = pyqtSignal(list)  # Signal to pass new data to the main GUI thread

    def __init__(self, sample_rate, mode, window_size, parent=None):
        super().__init__(parent)
        self.sample_rate = sample_rate
        self.running = True

        # mode == 0 > ACC only
        # mode == 1 > EDA and DAC only (always index 1)
        # mode == 2 > ALL (always index 1)

        self.index = 1

        self.window_size = window_size  # Number of samples for the moving average

        self.ma_buffer = []  # Unified buffer name for moving average

    def init_lsl_stream(self):
        streams = resolve_stream()
        self.inlet = StreamInlet(streams[0])

    def run(self):
        self.init_lsl_stream()

        while self.running:
            sample, _ = self.inlet.pull_sample(timeout=0.01)

            if sample:

                if self.window_size is not None:
                    # Append the current sample to the buffer
                    self.ma_buffer.append(sample[self.index])

                    # If the buffer exceeds the window size, remove the oldest sample
                    if len(self.ma_buffer) > self.window_size:
                        self.ma_buffer.pop(0)

                    # Calculate the moving average and emit the data
                    avg_sample = sum(self.ma_buffer) / len(self.ma_buffer)
                    self.signal.emit([avg_sample])
                else:
                    self.signal.emit([sample[self.index]])

            time.sleep(0.5 / (self.sample_rate))  # Adjust to the desired sample rate

    def stop(self):
        self.running = False
        self.quit()
        self.wait()  # Wait for the thread to finish
