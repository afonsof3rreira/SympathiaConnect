from PyQt5.QtCore import QThread, pyqtSignal
from pylsl import StreamInlet, resolve_stream
import time

class LSLDataWorker(QThread):
    signal_acc = pyqtSignal(list)  # Signal to pass new data to the main GUI thread
    signal_eda = pyqtSignal(list)  # Signal to pass new data to the main GUI thread
    signal_dac = pyqtSignal(list)  # Signal to pass new data to the main GUI thread

    def __init__(self, sample_rate, acc_enable, eda_enable, parent=None):
        super().__init__(parent)
        self.sample_rate = sample_rate
        self.running = True

        self.acc_enable = acc_enable
        self.eda_enable = eda_enable

    def init_lsl_stream(self):
        streams = resolve_stream()
        # Print out the names of the available streams
        print("Stream length: " + str(len(streams)))

        self.inlet = StreamInlet(streams[0])

    def run(self):
        self.init_lsl_stream()

        while self.running:

            sample, _ = self.inlet.pull_sample(timeout=0.01)
            if sample:

                print("samples: ")
                print(sample)

                if self.acc_enable and not self.eda_enable:
                    self.signal_acc.emit([sample[0]])  # Emit the new data to the main thread

                elif not self.acc_enable and self.eda_enable:
                    self.signal_eda.emit([sample[0]])  # Emit the new data to the main thread
                    self.signal_dac.emit([sample[1]])  # Emit the new data to the main thread

                elif self.acc_enable and self.eda_enable:
                    self.signal_acc.emit([sample[0]])  # Emit the new data to the main thread
                    self.signal_eda.emit([sample[1]])  # Emit the new data to the main thread
                    self.signal_dac.emit([sample[2]])  # Emit the new data to the main thread

            time.sleep(1 / (self.sample_rate))  # Adjust to the desired sample rate

    def stop(self):
        self.running = False
        self.quit()
        self.wait()  # Wait for the thread to finish
