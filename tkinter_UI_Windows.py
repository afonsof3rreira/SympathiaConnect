import inspect
import multiprocessing
import os
import tkinter as tk
import threading
from tkinter import messagebox
import darkdetect
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QApplication
from LSL_plotting_Windows import LSLPlotWindow, open_lsl_plot
from acquisition_Windows import Acquisition
from saving_preferences import saving_preferences, update_fields
from scientisst import *
from utilities import load_icon, get_root_project_path, colors, read_params, write_params, open_user_guide
from utils.input_validation import validate_time_in, validate_fs_in, validate_dac_in
from utils.scientisst_actions import led_pulse
from utils.bluetooth_MacOS import ConnectionStatus, get_available_ports
from PIL import ImageTk  # For working with images (e.g., PNG)


class App(tk.Frame):
    """
    Analog channels:
        AI1: Saturates
        AI2 -
        AI3 -
        AI4: low range
        AI5: Z axis accelerometer!
        AI6: testing
    """

    def __init__(self, master=None, version=None, root_path=None, os_type='Windows', icon_file=None, ld_theme=None):

        # TODO: Next steps: make the scientISST acquisition through the API be run in "parallel" (threading) with respect to the tkinter App so that its buttons don't freeze
        #  TODO: Integrate and test the button to generate the pulse signal

        super().__init__(master)

        self.scientisst = None

        self.os_type = os_type
        self.root_path = root_path
        self.version = version

        if ld_theme is None:
            self.ld_theme = "Light"
        else:
            self.ld_theme = ld_theme

        # Get the frame of the caller (the script calling this function)
        frame = inspect.stack()[1]
        # Get the filename (script name) from the frame
        script_name = frame[0].f_code.co_filename

        # Return the absolute path of the script
        current_script = os.path.abspath(script_name)

        parent_folder_path, _ = os.path.split(current_script)
        self.uparams_path = os.path.join(parent_folder_path, "user_parameters.txt")
        self.plot_process = None  # Initialize plot_process to None

        try:
            self.user_parameters = read_params(self.uparams_path)

        except:
            self.user_parameters = {
                "address": None,
                "fs": 20,
                "ACC_enable": True,
                "EDA_enable": True,
                "duration_h": 0,
                "duration_m": 1,
                "duration_s": 0,
                "verbose": None,
                "dac": 165,
                "auto_load_plot": True,
                "directory": ".",
                "naming": "Timestamp",
                "prefix": "",
                "suffix": ""
            }

        if os.path.exists(os.path.join(self.user_parameters["directory"], "Signals")):
            self.user_parameters["directory"] = os.path.join(self.user_parameters["directory"], "Signals")

        # Track the state of the checkbox
        self.view_plot_var = tk.BooleanVar(value=False)  # Initially off
        self.auto_load_plot_var = tk.BooleanVar(value=self.user_parameters['auto_load_plot'])

        self.master.protocol("WM_DELETE_WINDOW", lambda: self.on_closing())

        self.connection_status = ConnectionStatus.DISCONNECTED

        self.master = master
        self.master.grid_rowconfigure(0, weight=1)  # This row expands.
        self.master.grid_columnconfigure(0, weight=1)  # This column expands.
        self.master.configure(bg=colors[self.ld_theme]['Windows_bg'])
        self.configure(bg=colors[self.ld_theme]['Windows_bg'])

        self.create_menu()

        self.grid()
        self.grid_rowconfigure(0, weight=1)  # Make row 1 resizable
        self.grid_columnconfigure(0, weight=1)  # Make column 0 resizable

        # Create a frame to hold the image and title
        header_frame = tk.Frame(self, bg=colors[self.ld_theme]['Windows_bg'])
        header_frame.grid(row=1, column=0, columnspan=2, padx=10, sticky='nsew')

        header_frame.grid_rowconfigure(0, weight=1)
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=1)

        self.icon_file = icon_file

        # Load your image (PNG file)
        if icon_file is not None:
            img = icon_file.resize((50, 50))  # Resize the image (adjust size as needed)
            self.img_tk = ImageTk.PhotoImage(img)  # Convert to Tkinter-compatible format

        # Create a label with the image
        self.img_label = tk.Label(header_frame, image=self.img_tk, bg=colors[self.ld_theme]['Windows_bg'])
        self.img_label.grid(row=0, column=0)  # Add padding between image and text

        # Create a label with the title of the app
        self.title_label = tk.Label(header_frame, text="Sympathia Connect", font=('Roboto', 20, 'bold'),
                                    bg=colors[self.ld_theme]['Windows_bg'], fg=colors[self.ld_theme]['Windows_fg'])

        # Place the title next to the image
        self.title_label.grid(row=0, column=1)  # Add padding between title and

        self.row_offset = 3
        self.create_widgets()

    def setup_duration_boxes(self):
        # Label for Duration
        self.time_input_1_label = tk.Label(self, text="Duration (hh:mm:ss)", font=('Roboto', 14),
                                           bg=colors[self.ld_theme]['Windows_bg'],
                                           fg=colors[self.ld_theme]['Windows_fg'])
        self.time_input_1_label.grid(row=2 + self.row_offset, column=0, padx=10, pady=5)

        # Calculate hours, minutes, and seconds from the given duration in minutes
        if self.user_parameters['duration_h'] is not None:
            hours = self.user_parameters['duration_h']

        if self.user_parameters['duration_m'] is not None:
            minutes = self.user_parameters['duration_m']

        if self.user_parameters['duration_s'] is not None:
            seconds = self.user_parameters['duration_s']

        # Frame to hold the 3 Entry widgets for hours, minutes, and seconds
        self.time_input_frame = tk.Frame(self, bg=colors[self.ld_theme]['Windows_bg'])
        self.time_input_frame.grid(row=3 + self.row_offset, column=0, padx=5)

        # Entry for Hours
        self.hour_entry = tk.Entry(self.time_input_frame, width=5, validate="key",
                                   vcmd=(self.master.register(validate_time_in), '%P'), font=('Roboto', 12))
        self.hour_entry.insert(0, str(hours))  # Insert calculated hours
        self.hour_entry.grid(row=0 + self.row_offset, column=0, padx=2)

        # Entry for Minutes
        self.minute_entry = tk.Entry(self.time_input_frame, width=5, validate="key",
                                     vcmd=(self.master.register(validate_time_in), '%P'), font=('Roboto', 12))
        self.minute_entry.insert(0, str(minutes))  # Insert calculated minutes
        self.minute_entry.grid(row=0 + self.row_offset, column=1, padx=2)

        # Entry for Seconds
        self.second_entry = tk.Entry(self.time_input_frame, width=5, validate="key",
                                     vcmd=(self.master.register(validate_time_in), '%P'), font=('Roboto', 12))
        self.second_entry.insert(0, str(seconds))  # Insert calculated seconds
        self.second_entry.grid(row=0 + self.row_offset, column=2, padx=2)

    def create_menu(self):
        """ Creates the menu bar for the application """
        menubar = tk.Menu(self.master)

        # Adding View Menu
        self.view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='Plotting', menu=self.view_menu)

        self.view_menu.add_checkbutton(
            label='Auto-load',
            variable=self.auto_load_plot_var,
        )

        self.view_menu.add_command(
            label='Start window',
            command=self.launch_receive_and_plot  # Directly call the function you want
        )

        self.help_ = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='Settings', menu=self.help_)
        self.help_.add_command(label='Saving preferences', command=lambda: saving_preferences(self, self.ld_theme))
        self.help_.add_command(label='User Guide', command=self.open_user_guide)
        #self.help_.add_command(label='Check for Updates', command=self.update_checker.set_window)
        self.help_.add_command(label='About', command=self.show_about)
        self.master["menu"] = menubar

    def open_user_guide(self):
        pdf_path = os.path.join(self.root_path, "rsc", "Sympathia_Connect_User_Guide.pdf")
        open_user_guide(pdf_path)

    def toggle_mode(self):

        """Toggle between light and dark modes."""
        if self.ld_theme == 'Dark':
            self.ld_theme = 'Light'
        else:
            self.ld_theme = 'Dark'

    def show_about(self):
        """Display the About window."""
        messagebox.showinfo(
            "About",
            "Sympathia Connect\n"
            "Version: " + self.version + "\n\n"
            "Developed by Sympathia Technologies\n"
            "© 2024 Sympathia Technologies. All rights reserved.\n\n"
            "Made by those that use their head to live with heart.\n\n"
            "For support, contact us at: info@sympathiatech.com"
        )

    def update_bt_dropdown(self):

        # Get the latest Bluetooth devices list
        self.bt_devices_list = get_available_ports(self.os_type)

        # if dict is not empty
        if self.bt_devices_list:

            # if the previosuly used device is On, then it should be auto-selected
            for port_name in self.bt_devices_list:
                if self.user_parameters["address"] == port_name:
                    self.bt_var.set(port_name)

            # else, it should be the first showing up
            else:
                self.bt_var.set(self.bt_devices_list[0])

        # else, empty
        else:
            self.bt_var.set("No Dev. Found")
            self.bt_devices_list.append("No Dev. Found")

        print(self.bt_var.get())

        # Create OptionMenu with updated device list
        self.bt_dropdown = tk.OptionMenu(self, self.bt_var, *self.bt_devices_list, command=self.on_bt_selected)

        self.bt_dropdown.grid(row=1 + self.row_offset, column=1)
        self.bt_dropdown.config(font=('Roboto', 12, 'bold'))
        self.bt_dropdown.config(bg=colors[self.ld_theme]['Windows_bg'], fg=colors[self.ld_theme]['Windows_fg'],
                                activebackground=colors[self.ld_theme]['Windows_bg'],
                                activeforeground=colors[self.ld_theme]['Windows_fg'])

        # Bind <Button-1> event to dynamically update the list when dropdown is clicked
        self.bt_dropdown.bind("<Button-1>", self.on_dropdown_click)

    def on_dropdown_click(self, event):
        # Refresh dropdown menu options on click
        self.update_bt_dropdown()

    def on_bt_selected(self, selected_device):
        # This function is called when an option is selected in the OptionMenu
        print(f"Selected Bluetooth Device: {selected_device}")
        # Update the user parameters with the selected device

        self.user_parameters["address"] = selected_device

        # Optionally, set the bt_var to the selected device as well
        self.bt_var.set(selected_device)

    def create_widgets(self):

        self.sci_status_txt = tk.Label(self, text="Device Status:", font=('Roboto', 14),
                                       bg=colors[self.ld_theme]['Windows_bg'], fg=colors[self.ld_theme]['Windows_fg'])
        self.sci_status_txt.grid(row=0 + self.row_offset, column=0, columnspan=1, pady=20)

        self.sci_status_label = tk.Label(self, text="Disconnected", font=('Roboto', 14),
                                         foreground=colors[self.ld_theme]['status'][self.connection_status],
                                         bg=colors[self.ld_theme]['Windows_bg'])
        self.sci_status_label.grid(row=0 + self.row_offset, column=1, columnspan=1)

        # Create the COM port selection drop-down
        self.com_label = tk.Label(self, text="Select Device:", font=('Roboto', 14),
                                  bg=colors[self.ld_theme]['Windows_bg'], fg=colors[self.ld_theme]['Windows_fg'])
        self.com_label.grid(row=1 + self.row_offset, column=0, pady=10)
        self.com_var = tk.StringVar(self)

        # StringVar to store the selected Bluetooth device
        self.bt_var = tk.StringVar(self)

        # Initialize the dropdown menu
        self.update_bt_dropdown()

        # TextBox Creation
        self.setup_duration_boxes()

        self.sr_label = tk.Label(self, text="Sampling Rate (Hz)", font=('Roboto', 14),
                                 bg=colors[self.ld_theme]['Windows_bg'], fg=colors[self.ld_theme]['Windows_fg'])
        self.sr_label.grid(row=2 + self.row_offset, column=1)

        self.sr_entry = tk.Entry(self, width=5, validate="key", vcmd=(self.master.register(validate_fs_in), '%P'),
                                 font=('Roboto', 12))
        self.sr_entry.grid(row=3 + self.row_offset, column=1)

        if self.user_parameters['fs'] is not None:
            self.sr_entry.insert("1", self.user_parameters['fs'])

        # TODO: Check box for ACC and EDA

        # Label on top of the checkboxes
        self.checkbox_label = tk.Label(self, text="Channels", font=('Roboto', 14),
                                       bg=colors[self.ld_theme]['Windows_bg'], fg=colors[self.ld_theme]['Windows_fg'])
        self.checkbox_label.grid(row=4 + self.row_offset, column=0, pady=(10, 5))

        # Frame to hold the checkboxes and their label
        self.checkbox_frame = tk.Frame(self, bg=colors[self.ld_theme]['Windows_bg'])
        self.checkbox_frame.grid(row=5 + self.row_offset, column=0, rowspan=1)

        # ACC checkbox
        self.acc_var = tk.BooleanVar()  # This will hold the state of the ACC checkbox
        self.acc_checkbox = tk.Checkbutton(self.checkbox_frame, text="ACC", variable=self.acc_var,
                                           bg=colors[self.ld_theme]['Windows_bg'],
                                           fg=colors[self.ld_theme]['Windows_fg'], selectcolor=colors[self.ld_theme]['Windows_bg'],
                                           command=lambda: self.validate_checkboxes(self.acc_var, [self.eda_var]),
                                           activebackground=colors[self.ld_theme]['Windows_bg'],
                                           activeforeground=colors[self.ld_theme]['Windows_fg'],
                                           width=7,
                                           height=2,
                                           font=('Roboto', 12))

        self.acc_checkbox.grid(row=1 + self.row_offset, column=1, padx=5)

        # EDA checkbox
        self.eda_var = tk.BooleanVar()  # This will hold the state of the EDA checkbox
        self.eda_checkbox = tk.Checkbutton(self.checkbox_frame, text="EDA", variable=self.eda_var,
                                           command=lambda: (
                                               self.validate_checkboxes(self.eda_var, [self.acc_var]),
                                               self.toggle_dac()),
                                           bg=colors[self.ld_theme]['Windows_bg'],
                                           fg=colors[self.ld_theme]['Windows_fg'], selectcolor=colors[self.ld_theme]['Windows_bg'],
                                           activebackground=colors[self.ld_theme]['Windows_bg'],
                                           activeforeground=colors[self.ld_theme]['Windows_fg'],
                                           width=7,
                                           height=2,
                                           font=('Roboto', 12))

        self.eda_checkbox.grid(row=1 + self.row_offset, column=0, padx=5)

        # Set initial states based on user parameters
        if not self.user_parameters['ACC_enable'] and not self.user_parameters['EDA_enable']:
            self.user_parameters['EDA_enable'] = True

        self.acc_var.set(self.user_parameters['ACC_enable'])
        self.eda_var.set(self.user_parameters['EDA_enable'])

        self.dac_value_label = tk.Label(self, text="DAC Value", font=('Roboto', 14),
                                        bg=colors[self.ld_theme]['Windows_bg'], fg=colors[self.ld_theme]['Windows_fg'])

        self.dac_value_label.grid(row=4 + self.row_offset, column=1, pady=(10, 5))

        self.dac_value_entry = tk.Entry(self, width=5, validate="key",
                                        vcmd=(self.master.register(validate_dac_in), '%P'), font=('Roboto', 12))
        self.dac_value_entry.grid(row=5 + self.row_offset, column=1)

        if self.user_parameters["dac"] is not None:
            self.dac_value_entry.insert("1", self.user_parameters['dac'])

        # Create the start button
        self.start_button = tk.Button(self, text="Start Acquisition", command=self.start_experiment,
                                      font=('Roboto', 12))

        self.start_button.grid(row=6 + self.row_offset, column=0, pady=10)

        # Create the Pulse button
        self.pulse_button = tk.Button(self, text="Send Synch Pulse", command=lambda: led_pulse(self.ac_process.get_scientisst()),
                                      font=('Roboto', 12))
        self.pulse_button.grid(row=6 + self.row_offset, column=1, pady=10)
        self.pulse_button.config(state=tk.DISABLED)

    def toggle_dac(self):
        if self.eda_var.get():
            # Disable the entry
            self.dac_value_entry.config(state=tk.NORMAL)
        else:
            # Enable the entry
            self.dac_value_entry.config(state=tk.DISABLED)

    def validate_checkboxes(self, var_to_check, var_others):
        """Ensures at least one checkbox remains checked."""
        # Check if all checkboxes are unchecked
        if not var_to_check.get() and not any(var.get() for var in var_others):
            # Reset the variable to keep at least one checkbox checked
            var_to_check.set(True)
            print("At least one checkbox must be checked.")

    def update_connection_status(self):
        # state definitions
        # get status from the scientisst class
        if hasattr(self, 'ac_process') and self.ac_process:
            try:
                self.connection_status = self.ac_process.get_connection_status()

            except:
                pass

            if self.connection_status == ConnectionStatus.DISCONNECTED:
                self.sci_status_label.config(text="Disconnected",
                                             fg=colors[self.ld_theme]['status'][self.connection_status])

            elif self.connection_status == ConnectionStatus.CONNECTING:
                self.sci_status_label.config(text="Connecting",
                                             fg=colors[self.ld_theme]['status'][self.connection_status])

            elif self.connection_status == ConnectionStatus.CONNECTED:
                self.sci_status_label.config(text="Connected",
                                             fg=colors[self.ld_theme]['status'][self.connection_status])

            elif self.connection_status == ConnectionStatus.ACQUIRING:
                self.sci_status_label.config(text="Acquiring",
                                             fg=colors[self.ld_theme]['status'][self.connection_status])

            elif self.connection_status == ConnectionStatus.CONNECTION_FAILED:
                self.sci_status_label.config(text="Connection Failed",
                                             fg=colors[self.ld_theme]['status'][self.connection_status])

            elif self.connection_status == ConnectionStatus.ACQUISITION_FINISHED:
                self.sci_status_label.config(text="Acquisition Finished",
                                             fg=colors[self.ld_theme]['status'][self.connection_status])

        if self.connection_status == ConnectionStatus.ACQUIRING:

            self.pulse_button.config(state=tk.NORMAL)

            if self.view_menu.entrycget("Auto-load", "state") != tk.DISABLED:
                self.view_menu.entryconfig("Auto-load", state=tk.DISABLED)

            if self.view_menu.entrycget("Start window", "state") != tk.DISABLED and self.auto_load_plot_var.get():
                self.view_menu.entryconfig("Start window", state=tk.DISABLED)

            elif self.view_menu.entrycget("Start window", "state") != tk.NORMAL and not self.auto_load_plot_var.get():
                self.view_menu.entryconfig("Start window", state=tk.NORMAL)


        else:
            if self.pulse_button.cget("state") != tk.DISABLED:
                self.pulse_button.config(state=tk.DISABLED)

            if self.view_menu.entrycget("Auto-load", "state") != tk.NORMAL:
                self.view_menu.entryconfig("Auto-load", state=tk.NORMAL)

            if self.view_menu.entrycget("Start window", "state") != tk.DISABLED:
                self.view_menu.entryconfig("Start window", state=tk.DISABLED)

        if self.connection_status != ConnectionStatus.DISCONNECTED:
            self.start_button.config(state=tk.DISABLED)
        else:
            if self.start_button.cget("state") != tk.NORMAL:
                self.start_button.config(state=tk.NORMAL)


        self.after(200, self.update_connection_status)

    def start_experiment(self):

        print(self.user_parameters)

        if self.bt_var.get():
            update_fields(self)

            # first thing before actually starting is to save the json file
            try:
                self.overwrite_user_params()
            except:
                print("Could not overwrite User Params. Check if file exists")

            if self.auto_load_plot_var.get():
                self.ac_process = Acquisition(self.user_parameters, self.launch_receive_and_plot, self.close_plot)

            else:
                self.ac_process = Acquisition(self.user_parameters)

            acquisition_cycle_thread = threading.Thread(target=self.ac_process.acquisition_cycle, daemon=True)
            acquisition_cycle_thread.start()

    def on_closing(self):

        update_fields(self)

        try:
            self.overwrite_user_params()
        except Exception as e:
            print("Exception:", e)
            print("Error: could not save user parameters")

        if hasattr(self, 'ac_process') and self.ac_process is not None:
            try:
                self.ac_process.cleanup()
            except Exception as e:
                print("Error during cleanup:", e)

        print("closing event")
        self.master.destroy()

    def overwrite_user_params(self):
        """Overwrites the json data."""
        # with open(self.json_path, 'w') as fp:
        #     json.dump(self.user_parameters, fp)
        # self.
        write_params(self.uparams_path, self.user_parameters)

    def launch_receive_and_plot(self):

        if self.plot_process is not None:
            if self.plot_process.is_alive():
                print("Plotting process is already running - 9kph.")
                return

        self.plot_process = multiprocessing.Process(target=open_lsl_plot,
                                                    args=(self.user_parameters['fs'],
                                                          self.user_parameters['EDA_enable'],
                                                          self.user_parameters['ACC_enable'],
                                                          self.ld_theme))
        self.plot_process.start()
        print("Plotting process started.")

    def close_plot(self):
        """Close the plotting subprocess."""
        if self.plot_process is None or not self.plot_process.is_alive():
            print("No active plotting process to terminate.")
            return

        self.plot_process.terminate()
        self.plot_process.join()  # Clean up resources
        print("Plotting process terminated.")
        self.plot_process = None
        self.view_plot_var.set(0)  # Uncheck the box

class App_UI_Windows():

    def __init__(self, version, debug=False):

        root_path = get_root_project_path(debug=debug)
        rsc_path = os.path.join(root_path, 'rsc')

        root = tk.Tk()

        ld_theme = darkdetect.theme()  # Returns 'light' or 'dark'
        icon_img = load_icon(rsc_path, 'Windows', ld_theme=ld_theme)
        # Convert the image to a Tkinter compatible format

        # Set the window icon using 'wm' command
        root.tk.call('wm', 'iconphoto', root._w, ImageTk.PhotoImage(icon_img, master=root))
        root.rowconfigure(0, weight=1)
        root.title("Sympathia Connect")

        self.app = App(master=root, version=version, root_path=root_path, os_type='Windows', icon_file=icon_img, ld_theme=ld_theme)
        self.app.update_connection_status()

        root.geometry("500x475")  # Set the fixed size of the window (width x height)
        root.minsize(width=415, height=375)

    def get_app(self):
        return self.app

    def cleanup(self):
        self.app.on_closing()