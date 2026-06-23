import os
import time
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
import re

import winsound
from PIL import ImageTk
from utilities import get_root_project_path, load_icon


def generate_file_path(user_parameters: dict):

    prefix = user_parameters['prefix']
    suffix = user_parameters['suffix']

    if user_parameters["naming"] == 'Incremental':

        # Define regex pattern to match files with the specified prefix, number, and suffix
        pattern = re.compile(rf'^{re.escape(prefix)}(\d+){re.escape(suffix)}\.csv$')

        # Scan the directory and extract numbers from matching files
        existing_numbers = []
        for file_name in os.listdir(user_parameters["directory"]):

            match = pattern.match(file_name)
            if match:
                existing_numbers.append(int(match.group(1)))

        # Determine the next number
        next_number = max(existing_numbers, default=0) + 1

        # Construct the next file name
        output_filename = f"{prefix}{next_number}{suffix}.csv"
        return os.path.join(user_parameters['directory'], output_filename)

    else:  # i.e., Timestamp naming mode

        # time stamp for experiment folder and file path
        exp_time_stamp = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(time.time()))

        # Construct the next file name
        output_filename = f"{prefix}{exp_time_stamp}{suffix}.csv"
        return os.path.join(user_parameters['directory'], output_filename)


def sanitize_filename(filename):
    # Replace anything that's not a letter, number, dash, or underscore with an underscore
    return re.sub(r'[^a-zA-Z0-9_-]', '_', filename)


def update_fields(main_app):
    if main_app.acc_var.get() != main_app.user_parameters['ACC_enable']:
        main_app.user_parameters['ACC_enable'] = main_app.acc_var.get()

    if main_app.eda_var.get() != main_app.user_parameters['EDA_enable']:
        main_app.user_parameters['EDA_enable'] = main_app.eda_var.get()

    # First, check if any data in the text boxes is different from the ones in the input

    if int(main_app.hour_entry.get()) != main_app.user_parameters['duration_h']:
        main_app.user_parameters['duration_h'] = int(main_app.hour_entry.get())

    if int(main_app.minute_entry.get()) != main_app.user_parameters['duration_m']:
        main_app.user_parameters['duration_m'] = int(main_app.minute_entry.get())

    if int(main_app.second_entry.get()) != main_app.user_parameters['duration_s']:
        main_app.user_parameters['duration_s'] = int(main_app.second_entry.get())

    if int(main_app.sr_entry.get()) != main_app.user_parameters['fs']:
        main_app.user_parameters['fs'] = int(main_app.sr_entry.get())

    if int(main_app.dac_value_entry.get()) != main_app.user_parameters['dac']:
        main_app.user_parameters['dac'] = int(main_app.dac_value_entry.get())

    if main_app.bt_var.get() != main_app.user_parameters['address']:
        main_app.user_parameters['address'] = main_app.bt_var.get()

    if main_app.auto_load_plot_var.get() != main_app.user_parameters['auto_load_plot']:
        main_app.user_parameters['auto_load_plot'] = main_app.auto_load_plot_var.get()

    # Saving preferences are handled in the saving preferences window, not in the main window!


def saving_preferences(main_app, ld_mode):
    main_geometry = main_app.master.geometry()
    main_width, main_height, main_x, main_y = map(int, re.split(r'[x+]', main_geometry))

    # Define the size for the "Saving Preferences" window
    top_width = 450
    top_height = 450

    # Calculate the top-left corner to position the "Saving Preferences" window
    top_x = main_x
    top_y = main_y

    root_path = get_root_project_path()
    rsc_path = os.path.join(root_path, 'rsc')
    icon_img = load_icon(rsc_path, 'Windows', ld_theme=ld_mode)

    # Create a new Toplevel window for saving preferences
    top = tk.Toplevel(main_app.master)
    top.title("Saving Preferences")
    top.geometry(f"{top_width}x{top_height}+{top_x}+{top_y}")  # Use the calculated geometry

    top.transient(main_app.master)  # Keep it on top of the main window
    top.grab_set()  # Prevent interactions with other windows until closed

    top.tk.call('wm', 'iconphoto', top._w, ImageTk.PhotoImage(icon_img, master=top))

    # Directory selection
    dir_label_frame = tk.Frame(top)  # Use a frame for better alignment and grouping
    dir_label_frame.pack(pady=10)

    dir_label = tk.Label(dir_label_frame, text="Choose a directory to save files:", font=("Arial", 10, "bold"))
    dir_label.pack(anchor="w")  # Align text to the left for a professional look

    dir_label_hint = tk.Label(dir_label_frame, text="(Default: SympathiaConnect/Signals)", font=("Arial", 9, "italic"),
                              fg="gray")
    dir_label_hint.pack(anchor="w")  # Ali

    def select_directory():
        try:

            if main_app.user_parameters["directory"] and os.path.exists(main_app.user_parameters["directory"]):
                default_directory = main_app.user_parameters["directory"]


            elif os.path.exists(dir_entry.get()):
                default_directory = dir_entry.get()

            else:
                default_directory = os.path.join(get_root_project_path(debug=True), 'Signals')

            folder = filedialog.askdirectory(initialdir=default_directory, title="Select a Directory")

            if folder:
                dir_entry.delete(0, tk.END)
                dir_entry.insert(0, folder)
                update_filename_example()  # Update example when directory is selected

        except Exception as e:
            print(f"Error selecting directory: {e}")

    dir_button = tk.Button(top, text="Select Directory", command=select_directory)
    dir_button.pack()

    dir_entry = tk.Entry(top, width=80)
    dir_entry.pack(pady=10)

    # Naming options
    naming_label = tk.Label(top, text="Choose naming convention:")
    naming_label.pack(pady=10)

    naming_var = tk.StringVar(value="Timestamp")

    # Timestamp-based naming
    timestamp_rb = tk.Radiobutton(top, text="Timestamp-based", variable=naming_var, value="Timestamp")
    timestamp_rb.pack()

    # Incremental naming
    incremental_rb = tk.Radiobutton(top, text="Incremental naming", variable=naming_var, value="Incremental")
    incremental_rb.pack()

    # Provisional file name frame
    provisional_frame = tk.Frame(top, bg="lightgray", relief="sunken", bd=1)
    provisional_frame.pack(pady=10, fill="x", padx=20)

    # Provisional name label (left aligned)
    provisional_title = tk.Label(provisional_frame, text="Filename Preview: ", bg="lightgray", anchor="w")
    provisional_title.pack(side="left", padx=5, pady=5)

    # Provisional name value (centered)
    filename_label = tk.Label(provisional_frame, text="example.txt", bg="lightgray", anchor="center")
    filename_label.pack(side="left", padx=10, pady=5, expand=True)

    # Prefix and Suffix entry
    prefix_label = tk.Label(top, text="Optional prefix (leave blank if none):")
    prefix_label.pack(pady=5)

    # Validate prefix and suffix inputs for allowed characters (letters, numbers, dash, and underscore)
    def validate_input(P, max_length=20):  # Set max length here
        if len(P) <= max_length and re.match(r'^[a-zA-Z0-9_-]*$', P):
            return True
        else:
            return False

    vcmd = top.register(validate_input)

    prefix_entry = tk.Entry(top, width=20, validate="key", validatecommand=(vcmd, '%P'))
    prefix_entry.pack(pady=5)

    suffix_label = tk.Label(top, text="Optional suffix (leave blank if none):")
    suffix_label.pack(pady=5)

    suffix_entry = tk.Entry(top, width=20, validate="key", validatecommand=(vcmd, '%P'))
    suffix_entry.pack(pady=5)

    if main_app.user_parameters["directory"] and os.path.isdir(main_app.user_parameters["directory"]):
        main_app.user_parameters["directory"] = os.path.join(get_root_project_path(debug=True), 'Signals')
        dir_entry.insert(0, main_app.user_parameters["directory"])

    else:
        main_app.user_parameters["directory"] = os.path.join(get_root_project_path(debug=True), 'Signals')
        dir_entry.insert(0, main_app.user_parameters["directory"])

    if main_app.user_parameters["naming"]:
        if main_app.user_parameters["naming"] == 'Incremental':
            naming_var.set('Incremental')
        else:
            naming_var.set('Timestamp')

    if main_app.user_parameters["prefix"]:
        prefix_entry.insert(0, main_app.user_parameters["prefix"])

    if main_app.user_parameters["suffix"]:
        suffix_entry.insert(0, main_app.user_parameters["suffix"])

    # Update the provisional filename example dynamically
    def update_filename_example():
        # Get values from the entries and naming convention
        save_dir = dir_entry.get()
        prefix = prefix_entry.get()
        suffix = suffix_entry.get()
        naming_choice = naming_var.get()

        # Sanitize prefix and suffix to ensure no invalid characters
        prefix = sanitize_filename(prefix)
        suffix = sanitize_filename(suffix)

        # Generate the example filename based on the naming convention
        if naming_choice == "Timestamp":
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"{prefix}{timestamp}{suffix}.csv"

        elif naming_choice == "Incremental":
            filename = f"{prefix}0001{suffix}.csv"
        else:
            filename = f"{prefix}{suffix}.csv"  # Default case

        # Update the filename label with the provisional filename
        filename_label.config(text=filename)

        # Update preferences in the main app
        if os.path.isdir(save_dir):
            main_app.user_parameters["directory"] = save_dir
        main_app.user_parameters["naming"] = naming_choice
        main_app.user_parameters["prefix"] = prefix
        main_app.user_parameters["suffix"] = suffix

    # Bind the update function to the entry fields and naming radio buttons
    prefix_entry.bind("<KeyRelease>", lambda event: update_filename_example())
    suffix_entry.bind("<KeyRelease>", lambda event: update_filename_example())
    naming_var.trace("w", lambda *args: update_filename_example())
    dir_entry.bind("<KeyRelease>", lambda event: update_filename_example())

    update_filename_example()
