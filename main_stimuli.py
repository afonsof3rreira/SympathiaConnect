import csv
import inspect
import json
import os
import serial
import time
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import sys
from scientisst import *
from scientisst import __version__
from threading import Timer
from threading import Event
from sense_src.arg_parser import ArgParser
from sense_src.custom_script import get_custom_script, CustomScript
from sense_src.device_picker import DevicePicker
from sense_src.file_writer import *
import subprocess

print(tk.TkVersion)

def run_scheduled_task(duration, stop_event):
    def stop(stop_event):
        stop_event.set()

    timer = Timer(duration, stop, [stop_event])
    timer.start()
    return timer

class App(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)

        # Get the frame of the caller (the script calling this function)
        frame = inspect.stack()[1]
        # Get the filename (script name) from the frame
        script_name = frame[0].f_code.co_filename

        # Return the absolute path of the script
        current_script = os.path.abspath(script_name)

        parent_folder_path, _ = os.path.split(current_script)
        self.json_path = os.path.join(parent_folder_path, "prev_args.json")

        try:
            with open(self.json_path, 'r') as fp:
                self.user_parameters = json.load(fp)
        except:
            self.user_parameters = {
                "address": None,
                "fs": 20,
                "channels": None, # TODO: add channels in such a way
                "duration_m": 1,
                "duration_s": 0,
                "lsl": None,
                "quiet": None,
                "version": None,
                "verbose": None,
                "dac": None
            }

        self.master.protocol("WM_DELETE_WINDOW", lambda: self.on_closing())

        self.master = master
        self.grid()

        self.create_widgets()

    def create_widgets(self):
        # Create the COM port selection drop-down
        self.com_label = tk.Label(self, text="Select COM Port:")
        self.com_label.grid(row=0, column=0)
        self.com_var = tk.StringVar(self)
        self.com_var.set("")  # default value
        self.com_dropdown = tk.OptionMenu(self, self.com_var, *self.get_available_ports(), "", command=self.select_port)
        self.com_dropdown.grid(row=0, column=1)

        # TODO: Duration needs to become hour - minute - second
        # self.time_input_1_label = tk.Label(self, text="Duration")
        # self.time_input_1_label.grid(row=1, column=0)
        #
        # self.time_input_1 = tk.Text(self, height=1, width=5)
        #
        # if self.user_parameters['duration_m'] is not None:
        #     self.time_input_1.insert("1.0", self.user_parameters['duration_m'])
        #
        # self.time_input_1.grid(row=2, column=0)


        self.time_input_2_label = tk.Label(self, text="Sampling rate")
        self.time_input_2_label.grid(row=1, column=1)

        self.time_input_2 = tk.Text(self, height=1, width=5)
        self.time_input_2.grid(row=2, column=1)

        if self.user_parameters['fs'] is not None:
            self.time_input_2.insert("1.0", self.user_parameters['fs'])

        self.enabled_channels_label = tk.Label(self, text="Channels list")
        self.enabled_channels_label.grid(row=3, column=0)

        self.enabled_channels = tk.Text(self, height=1, width=15)
        self.enabled_channels.grid(row=4, column=0)

        self.dac_value_label = tk.Label(self, text="DAC value")
        self.dac_value_label.grid(row=3, column=1)

        self.dac_value = tk.Text(self, height=1, width=5)
        self.dac_value.grid(row=4, column=1)

        if self.user_parameters['channels'] is not None:
            self.enabled_channels.insert("1.0", self.user_parameters['channels'])

        if self.user_parameters["dac"] is not None:
            self.dac_value.insert("1.0", self.user_parameters['dac'])

        # Create the start button
        self.start_button = tk.Button(self, text="Start Transmission", command=self.start_experiment)
        self.start_button.grid(row=5, columnspan=2)
        self.i = 0

    def select_port(self, widget):

        self.com_port = self.com_var.get()
        print(self.com_port)

        if not self.com_port:
            tk.messagebox.showerror("Error", "Please select a COM port")
            return

    def get_available_ports(self):
        # Returns a list of available COM ports
        available_ports = []
        for i in range(256):
            try:
                ser = serial.Serial("COM{}".format(i))
                available_ports.append(ser.portstr)
                ser.close()
            except serial.SerialException:
                pass

        available_ports.append("/dev/tty.ScientISST-A0:EE")
        available_ports.append("/dev/tty.ScientISST-A-5A")
        available_ports.append("/dev/tty.ScientISST-DF-E")
        available_ports.append("/dev/tty.ScientISST-F-96")
        available_ports.append("/dev/tty.ScientISST-3-A6")
        available_ports.append("/dev/tty.ScientISST-4-E")


        return available_ports

    def choose_file(self):
        # Opens a file dialog to select a CSV file
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        self.file_label.configure(text=f"Selected File: {file_path}")
        self.file_path = file_path

    def start_experiment(self):

        if isinstance(self.com_port, str):

            arg_parser = ArgParser()
            args = arg_parser.args

            # First, check if any data in the text boxes is different from the ones in the input
            if int(self.time_input_1.get(1.0, "end-1c")) != self.user_parameters['duration']:
                self.user_parameters['duration'] = int(self.time_input_1.get(1.0, "end-1c"))

            if int(self.time_input_2.get(1.0, "end-1c")) != self.user_parameters['fs']:
                self.user_parameters['fs'] = int(self.time_input_2.get(1.0, "end-1c"))

            if float(self.dac_value.get(1.0, "end-1c")) != self.user_parameters['dac']:
                self.user_parameters['dac'] = float(self.dac_value.get(1.0, "end-1c"))

            def are_all_integers(lst):
                for item in lst:
                    if not isinstance(item, int):
                        return False
                return True

            try:
                input_channels_str = self.enabled_channels.get(1.0, "end-1c").split(",")
                input_channels_list = [int(num) for num in input_channels_str]
                if are_all_integers(input_channels_list):
                    self.user_parameters['channels'] = self.enabled_channels.get(1.0, "end-1c")

            except:
                pass

            if int(self.time_input_2.get(1.0, "end-1c")) != self.user_parameters['fs']:
                self.user_parameters['fs'] = int(self.time_input_2.get(1.0, "end-1c"))

            print("com port is")
            print(self.com_port)
            print(self.user_parameters)

            if self.com_port != self.user_parameters['address']:
                self.user_parameters['address'] = self.com_port

            # ORIGINAL CODE...
            if self.user_parameters["version"]:
                sys.stdout.write("sense.py version {}\n".format(__version__))
                sys.exit(0)

            if self.user_parameters["address"]:
                address = self.user_parameters["address"]

            else:
                address = DevicePicker().select_device()
                if not address:
                    arg_parser.error("No paired device found")
                else:
                    arg_parser.error("No address provided")

            self.user_parameters["channels"] = sorted(map(int, self.user_parameters["channels"].split(",")))

            # TODO: Re-update all fields

            # address, fs, duration OK
            print(address)

            scientisst = ScientISST(address, com_mode='bt_classic', log=True)

            scientisst.dac(self.user_parameters['dac'], pwm=True)

            try:
                if self.user_parameters["output"]:
                    firmware_version = scientisst.version_and_adc_chars(print=True)
                    file_writer = FileWriter(
                        self.user_parameters["output"],
                        address,
                        self.user_parameters["fs"],
                        self.user_parameters["channels"],
                        mv=False,
                        api_version=__version__,
                        firmware_version=firmware_version,
                    )

                if self.user_parameters["lsl"]:
                    from sense_src.stream_lsl import StreamLSL

                    lsl = StreamLSL(
                        self.user_parameters["channels"],
                        self.user_parameters["fs"],
                        address,
                    )

                stop_event = Event()

                scientisst.start(self.user_parameters["fs"], self.user_parameters["channels"])
                sys.stdout.write("Start acquisition\n")

                # TODO: Initiate window within 2 seconds
                rt_plot = threading.Thread(self.launch_receive_and_plot())
                rt_plot.start()

                if self.user_parameters["output"]:
                    file_writer.start()
                if self.user_parameters["lsl"]:
                    lsl.start()

                timer = None
                if self.user_parameters["duration"] > 0:
                    timer = run_scheduled_task(self.user_parameters["duration"], stop_event)

                tick = 0

                try:
                    if self.user_parameters["verbose"]:
                        header = "\t".join(get_header(self.user_parameters["channels"], self.user_parameters["raw"])) + "\n"
                        sys.stdout.write(header)

                    while not stop_event.is_set():
                        frames = scientisst.read(convert=self.user_parameters["raw"], curr_dac_value=self.user_parameters["dac"])

                        self.user_parameters["dac"] = scientisst.dac_control(self.user_parameters["dac"], frames, tick)

                        if self.user_parameters["output"]:
                            file_writer.put(frames)
                        if self.user_parameters["lsl"]:
                            lsl.put(frames)
                        if self.user_parameters["script"]:
                            script.put(frames)
                        if self.user_parameters["verbose"]:
                            sys.stdout.write("{}\n".format(frames[0]))

                        tick += 1
                except KeyboardInterrupt:
                    if self.user_parameters["duration"] and timer:
                        timer.cancel()
                    pass

                scientisst.stop()
                # let the acquisition stop before stoping other threads
                time.sleep(0.25)

                sys.stdout.write("Stop acquisition\n")
                if self.user_parameters["output"]:
                    file_writer.stop()
                if self.user_parameters["lsl"]:
                    lsl.stop()
                if self.user_parameters["script"]:
                    script.stop()

            finally:
                scientisst.disconnect()

            sys.exit(0)

        else:
            Warning("COM PORT not selected.")

    def on_closing(self):

        with open(self.json_path, 'w') as fp:
            json.dump(self.user_parameters, fp)

        self.master.destroy()

    def launch_receive_and_plot(self):
        print("Launching plot------------------------")
        time.sleep(1)

        try:
            subprocess.Popen(["python", "-m", "pylsl.examples.ReceiveAndPlot"])
        except subprocess.CalledProcessError as e:
            print("Error:", e)



if __name__ == '__main__':
    root = tk.Tk()
    root.title("Experiment")

    app = App(master=root)
    app.mainloop()
