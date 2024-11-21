import sys
import threading
import time
import traceback
from threading import Event, Timer
from scientisst import ScientISST, __version__
from sense_src.device_picker import DevicePicker
from sense_src.file_writer import FileWriter, get_header
from utilities import compute_time_seconds
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

    def __init__(self, user_parameters: dict, plot_thread_callback):
        self.user_parameters = user_parameters
        self.plot_thread_callback = plot_thread_callback

    def get_connection_status(self):
        return self.connection_status

    def acquisition_cycle(self, start_exp_btn):

        self.connection_error = True
        self.start_exp_btn = start_exp_btn

        self.start_exp_btn.config(state=tk.DISABLED)

        first_acquisition = True
        ac_index = 0

        while ac_index < 2:

            try:
                # time stamp for experiment folder and file path
                exp_time_stamp = time.localtime(time.time())

                # create experiment folder and file path
                folder_path, time_str = create_exp_folder(exp_time_stamp)
                file_path = os.path.join(folder_path, time_str + '.csv')

                self.start_acquisition(first_acquisition, folder_path, file_path)
                ac_index = 2

            except Exception as e:
                traceback.print_exc()
                clean_up_folder(folder_path, file_path)
                ac_index += 1

            if self.connection_error:
                print("Connection Error")

            else:
                first_acquisition = False

        self.connection_status = ConnectionStatus.DISCONNECTED
        self.start_exp_btn.config(state=tk.NORMAL)


    def start_acquisition(self, first_acquisition, folder_path, file_path):

        print(self.user_parameters)

        if self.user_parameters["address"]:
            address = self.user_parameters["address"]
            print(address)

        else:
            address = DevicePicker().select_device()

        channels = []
        if self.user_parameters['ACC_enable']:
            channels.append(5)

        if self.user_parameters['EDA_enable']:
            channels.append(7)

        print("Channels are: ")
        print(channels)

        # TODO: Re-update all fields

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

            if self.user_parameters["lsl"]:
                from sense_src.stream_lsl import StreamLSL


                lsl = StreamLSL(
                    channels,
                    self.user_parameters["fs"],
                    address,
                    eda_enable=self.user_parameters["EDA_enable"],
                )

            self.scientisst.start(self.user_parameters["fs"], channels)

            self.connection_status = ConnectionStatus.ACQUIRING
            sys.stdout.write("Start acquisition\n")

            # Launch plot
            if first_acquisition and self.plot_thread_callback:
                rt_plot = threading.Thread(target=self.plot_thread_callback)
                rt_plot.start()

            if file_path:
                file_writer.start()

            if self.user_parameters["lsl"]:
                lsl.start()

            tick = 0

            # DO CYCLE
            stop_event = Event()


            timer = None
            acquisition_time = compute_time_seconds(self.user_parameters)

            if timer is not None:
                timer = run_scheduled_task(acquisition_time, stop_event)

            try:
                if self.user_parameters["verbose"]:
                    header = "\t".join(get_header(channels, False)) + "\n"
                    sys.stdout.write(header)

                while not stop_event.is_set():

                    if 7 in channels:
                        frames = self.scientisst.read(convert=False, curr_dac_value=self.user_parameters["dac"])

                        idx_to_extract = 6 + len(channels) - 1

                        self.user_parameters["dac"] = self.scientisst.dac_control(self.user_parameters["dac"], frames, tick,
                                                                                  idx_to_extract=idx_to_extract)
                    else:
                        frames = self.scientisst.read(convert=False)

                    if file_path:
                        file_writer.put(frames)

                    if self.user_parameters["lsl"]:
                        lsl.put(frames)

                    if self.user_parameters["verbose"]:
                        sys.stdout.write("{}\n".format(frames[0]))

                    tick += 1

            except KeyboardInterrupt:
                if acquisition_time and timer:
                    timer.cancel()

            self.scientisst.stop()
            # let the acquisition stop before stoping other threads
            time.sleep(0.25)

            self.connection_status = ConnectionStatus.CONNECTED
            sys.stdout.write("Stop acquisition\n")

            if file_path:
                file_writer.stop()
            if self.user_parameters["lsl"]:
                lsl.stop()

        finally:
            clean_up_folder(folder_path, file_path)

            # # TODO: Let's not disconnect
            self.scientisst.disconnect()
            self.connection_status = ConnectionStatus.DISCONNECTED
            pass

        sys.exit(0)



