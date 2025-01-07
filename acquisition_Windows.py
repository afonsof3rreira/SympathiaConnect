import sys
import threading
import time
import traceback
from threading import Event, Timer

import winsound

from saving_preferences import generate_file_path
from scientisst import ScientISST, __version__
from sense_src.device_picker import DevicePicker
from sense_src.file_writer import FileWriter, get_header
from utilities import compute_time_seconds, check_time_is_notNull
from utils.bluetooth_MacOS import ConnectionStatus, _reset_BT, hard_bt_reconnect
import os
from utils.data import create_exp_folder, clean_up_folder
import tkinter as tk

def run_scheduled_task(duration, stop_event):
    def stop(stop_event):
        stop_event.set()

    timer = Timer(duration, stop, [stop_event])
    timer.start()
    return timer

class Acquisition:
    """Class for the acquisition cycle and process."""

    def __init__(self, user_parameters: dict, plot_thread_callback=None, close_plot=None):
        self.connection_status = None
        self.user_parameters = user_parameters
        self.plot_thread_callback = plot_thread_callback
        self.close_plot = close_plot

    def get_connection_status(self):
        return self.connection_status

    def acquisition_cycle(self):

        self.connection_error = True

        first_acquisition = True
        ac_index = 0
        limit_index = 1

        while ac_index <= limit_index:

            try:

                # time stamp for experiment folder and file path
                exp_time_stamp = time.localtime(time.time())

                # create experiment folder and file path
                folder_path = self.user_parameters["directory"]
                file_path = generate_file_path(self.user_parameters)

                self.start_acquisition(first_acquisition, folder_path, file_path)
                ac_index = limit_index + 1
                self.connection_error = False

            except Exception as e:
                traceback.print_exc()
                try:
                    clean_up_folder(folder_path, file_path)
                except:
                    pass
                ac_index += 1

            if self.connection_error:
                print("Connection Error")

            else:
                first_acquisition = False

        if self.connection_error:
            self.emit_brief_status(ConnectionStatus.CONNECTION_FAILED, 1000)

    def emit_brief_status(self, status, duration_ms, sound=True):
        self.connection_status = status
        time.sleep(duration_ms / 1000)
        self.connection_status = ConnectionStatus.DISCONNECTED

        if sound:
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)

    def start_acquisition(self, first_acquisition, folder_path, file_path):

        global rt_plot
        print(self.user_parameters)

        if self.user_parameters["address"]:
            address = self.user_parameters["address"]

        else:
            address = DevicePicker().select_device()

        channels = []
        if self.user_parameters['ACC_enable']:
            channels.append(1)
            # channels.append(2) not yet working well
            channels.append(3)

        if self.user_parameters['EDA_enable']:
            channels.append(7)

        # address, fs, duration OK
        self.connection_status = ConnectionStatus.CONNECTING

        self.scientisst = ScientISST(address, com_mode="bt_classic", log=True,
                                     connection_error=self.connection_error)

        self.connection_status = ConnectionStatus.CONNECTED

        self.scientisst.dac(self.user_parameters['dac'], pwm=True)

        try:
            if file_path:
                firmware_version = self.scientisst.version_and_adc_chars(print=True)
                file_writer = FileWriter(
                    file_path,
                    address,
                    self.user_parameters["fs"],
                    channels,
                    mv=False,
                    api_version=__version__,
                    firmware_version=firmware_version,
                )

            from sense_src.stream_lsl import StreamLSL

            lsl = StreamLSL(
                self.user_parameters["fs"],
                address,
                eda_enable=self.user_parameters["EDA_enable"],
                acc_enable=self.user_parameters["ACC_enable"]
            )

            self.scientisst.start(self.user_parameters["fs"], channels)

            self.connection_status = ConnectionStatus.ACQUIRING
            sys.stdout.write("Start acquisition\n")

            # Launch plot
            if first_acquisition and self.plot_thread_callback:
                self.plot_thread_callback()

            if file_path:
                file_writer.start()

            lsl.start()

            tick = 0

            # DO CYCLE
            stop_event = Event()


            timer = None
            acquisition_time = compute_time_seconds(self.user_parameters)

            if check_time_is_notNull(self.user_parameters):
                timer = run_scheduled_task(acquisition_time, stop_event)

            try:
                if self.user_parameters["verbose"]:
                    header = "\t".join(get_header(channels)) + "\n"
                    sys.stdout.write(header)

                while not stop_event.is_set():

                    if 7 in channels:
                        frames = self.scientisst.read(convert=False, curr_dac_value=self.user_parameters["dac"])

                        idx_to_extract = 2

                        self.user_parameters["dac"] = self.scientisst.dac_control(self.user_parameters["dac"], frames, tick,
                                                                                  idx_to_extract=idx_to_extract)
                    else:
                        frames = self.scientisst.read(convert=False)

                    if file_path:
                        file_writer.put(frames)

                    lsl.put(frames)

                    if self.user_parameters["verbose"]:
                        sys.stdout.write("{}\n".format(frames[0]))

                    tick += 1

            except KeyboardInterrupt:
                if acquisition_time and timer:
                    timer.cancel()

            if self.close_plot is not None:
                self.close_plot()
            self.scientisst.stop()
            # let the acquisition stop before stopping other threads
            time.sleep(0.25)
            sys.stdout.write("Stop acquisition\n")

            if file_path:
                file_writer.stop()
            lsl.stop()

            self.emit_brief_status(ConnectionStatus.ACQUISITION_FINISHED, 1000)

        finally:
            if os.path.exists(file_path):
                clean_up_folder(folder_path, file_path)
            self.scientisst.disconnect()
            pass

        sys.exit(0)



