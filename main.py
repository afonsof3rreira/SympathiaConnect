import csv
import glob
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
                self.prev_data = json.load(fp)
        except:
            self.prev_data = {
                "address": None,
                "fs": None,
                "channels": None,
                "duration": None,
                "output": None,
                "raw": None,
                "lsl": None,
                "script": None,
                "quiet": None,
                "version": None,
                "verbose": None,
                "mode": None,
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

        print(self.prev_data['address'])
        if self.prev_data['address'] is not None:
            self.com_var.set(self.prev_data['address'])
        else:
            self.com_var.set("")  # default value

        self.com_dropdown = tk.OptionMenu(self, self.com_var, *self.get_available_ports(), command=self.select_port)
        self.com_dropdown.grid(row=0, column=1)

        # TextBox Creation
        self.duration_label = tk.Label(self, text="Duration (seconds)")
        self.duration_label.grid(row=1, column=0)

        self.duration_entry = tk.Text(self, height=1, width=5)

        if self.prev_data['duration'] is not None:
            self.duration_entry.insert("1.0", self.prev_data['duration'])

        self.duration_entry.grid(row=2, column=0)

        self.sr_label = tk.Label(self, text="Sampling rate (Hz)")
        self.sr_label.grid(row=1, column=1)

        self.sr_entry = tk.Text(self, height=1, width=5)
        self.sr_entry.grid(row=2, column=1)

        if self.prev_data['fs'] is not None:
            self.sr_entry.insert("1.0", self.prev_data['fs'])

        self.channels_label = tk.Label(self, text="Channels list (e.g. 1,2,3)")
        self.channels_label.grid(row=3, column=0)

        def validate_channels(new_value):
            if new_value == "":
                return True
            if all(part.isdigit() for part in new_value.split(',')):
                return True
            return False

        self.channels_entry = tk.Text(self, height=1, width=15)
        self.channels_entry.grid(row=4, column=0)

        if self.prev_data['channels'] is not None:
            self.channels_entry.insert("1.0", self.prev_data['channels'])

        self.dac_value_label = tk.Label(self, text="DAC value")
        self.dac_value_label.grid(row=3, column=1)

        self.dac_value_entry = tk.Text(self, height=1, width=5)
        self.dac_value_entry.grid(row=4, column=1)

        if self.prev_data["dac"] is not None:
            self.dac_value_entry.insert("1.0", self.prev_data['dac'])

        # Create the start button
        self.start_button = tk.Button(self, text="Start Transmission", command=self.start_experiment)
        self.start_button.grid(row=5, columnspan=2)
        self.i = 0

    def select_port(self, widget):

        # store the new COM PORT
        self.prev_data['address'] = self.com_var.get()

        if not self.com_var.get():
            tk.messagebox.showerror("Error", "Please select a COM port")
            return

    def get_available_ports(self):
        # Returns a list of available COM ports
        available_ports = []

        # Windows
        for i in range(256):
            try:
                ser = serial.Serial("COM{}".format(i))
                available_ports.append(ser.portstr)
                ser.close()
            except serial.SerialException:
                pass

        # Linux
        # List all the available serial ports
        ports = glob.glob('/dev/tty.*') + glob.glob('/dev/cu.*')

        for port in ports:
            try:
                ser = serial.Serial(port)
                available_ports.append(ser.portstr)
                ser.close()
            except serial.SerialException:
                pass

        # available_ports.append("/dev/tty.ScientISST-A0:EE")
        # available_ports.append("/dev/tty.ScientISST-A-5A")
        # available_ports.append("/dev/tty.ScientISST-DF-E")
        # available_ports.append("/dev/tty.ScientISST-F-96")
        # available_ports.append("/dev/tty.ScientISST-3-A6")
        # available_ports.append("/dev/tty.ScientISST-4-E")
        # available_ports.append("/dev/tty.ScientISST-282E")

        return available_ports

    def choose_file(self):
        # Opens a file dialog to select a CSV file
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        self.file_label.configure(text=f"Selected File: {file_path}")
        self.file_path = file_path

    def start_experiment(self):


        print("over-written")

        if isinstance(self.com_var.get(), str):

            arg_parser = ArgParser()
            args = arg_parser.args


            # First, check if any data in the text boxes is different from the ones in the input
            if int(self.duration_entry.get(1.0, "end-1c")) != self.prev_data['duration']:
                self.prev_data['duration'] = int(self.duration_entry.get(1.0, "end"))

            if int(self.sr_entry.get(1.0, "end-1c")) != self.prev_data['fs']:
                self.prev_data['fs'] = int(self.sr_entry.get(1.0, "end"))

            if int(self.dac_value_entry.get(1.0, "end-1c")) != self.prev_data['dac']:
                self.prev_data['dac'] = int(self.dac_value_entry.get(1.0, "end"))

            def are_all_integers(lst):
                for item in lst:
                    if not isinstance(item, int):
                        return False
                return True

            try:
                input_channels_str = self.channels_entry.get(1.0, "end").replace("\n", "").split(",")
                input_channels_list = [int(num) for num in input_channels_str]
                if are_all_integers(input_channels_list):
                    self.prev_data['channels'] = self.channels_entry.get(1.0, "end").replace("\n", "")

            except:
                pass

            if self.com_var.get() != self.prev_data['address']:
                self.prev_data['address'] = self.com_var.get()

            # first thing before actually starting is to save the json file
            self.overwrite_jsonfile()

            # ORIGINAL CODE...
            if self.prev_data["version"]:
                sys.stdout.write("sense.py version {}\n".format(__version__))
                sys.exit(0)

            if self.prev_data["address"]:
                address = self.prev_data["address"]

            else:
                if self.prev_data["mode"] == COM_MODE_BT:
                    address = DevicePicker().select_device()
                    if not address:
                        arg_parser.error("No paired device found")
                else:
                    arg_parser.error("No address provided")

            self.prev_data["channels"] = sorted(map(int, self.prev_data["channels"].split(",")))

            # TODO: Re-update all fields

            # address, fs, duration OK
            print(address)

            scientisst = ScientISST(address, com_mode=self.prev_data["mode"], log=True)

            scientisst.dac(self.prev_data['dac'], pwm=True)
            # scientisst.trigger([1, 2])

            try:
                if self.prev_data["output"]:
                    firmware_version = scientisst.version_and_adc_chars(print=True)
                    file_writer = FileWriter(
                        self.prev_data["output"],
                        address,
                        self.prev_data["fs"],
                        self.prev_data["channels"],
                        self.prev_data["raw"],
                        __version__,
                        firmware_version,
                    )

                if self.prev_data["lsl"]:
                    from sense_src.stream_lsl import StreamLSL

                    lsl = StreamLSL(
                        self.prev_data["channels"],
                        self.prev_data["fs"],
                        address,
                    )

                if self.prev_data["script"]:
                    script = get_custom_script(self.prev_data["script"])

                stop_event = Event()

                scientisst.start(self.prev_data["fs"], self.prev_data["channels"])
                sys.stdout.write("Start acquisition\n")

                # TODO: Initiate window within 2 seconds
                rt_plot = threading.Thread(self.launch_receive_and_plot())
                rt_plot.start()

                if self.prev_data["output"]:
                    file_writer.start()
                if self.prev_data["lsl"]:
                    lsl.start()
                if self.prev_data["script"]:
                    script.start()

                timer = None
                if self.prev_data["duration"] > 0:
                    timer = run_scheduled_task(self.prev_data["duration"], stop_event)

                tick = 0

                try:
                    if self.prev_data["verbose"]:
                        header = "\t".join(get_header(self.prev_data["channels"], self.prev_data["raw"])) + "\n"
                        sys.stdout.write(header)

                    while not stop_event.is_set():
                        frames = scientisst.read(convert=self.prev_data["raw"], curr_dac_value=self.prev_data["dac"])

                        self.prev_data["dac"] = scientisst.dac_control(self.prev_data["dac"], frames, tick)
                        # scientisst.trigger([1, 2])

                        if self.prev_data["output"]:
                            file_writer.put(frames)
                        if self.prev_data["lsl"]:
                            lsl.put(frames)
                        if self.prev_data["script"]:
                            script.put(frames)
                        if self.prev_data["verbose"]:
                            sys.stdout.write("{}\n".format(frames[0]))

                        tick += 1
                except KeyboardInterrupt:
                    if self.prev_data["duration"] and timer:
                        timer.cancel()
                    pass

                scientisst.stop()
                # let the acquisition stop before stoping other threads
                time.sleep(0.25)

                sys.stdout.write("Stop acquisition\n")
                if self.prev_data["output"]:
                    file_writer.stop()
                if self.prev_data["lsl"]:
                    lsl.stop()
                if self.prev_data["script"]:
                    script.stop()

            finally:
                scientisst.disconnect()

            sys.exit(0)

        else:
            Warning("COM PORT not selected.")

    def on_closing(self):
        self.overwrite_jsonfile()
        self.master.destroy()

    def overwrite_jsonfile(self):
        """Overwrites the json data."""

        with open(self.json_path, 'w') as fp:
            json.dump(self.prev_data, fp)

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
