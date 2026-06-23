import platform
from PIL import Image
import os
import sys
import subprocess
import sys
from utils.bluetooth_MacOS import ConnectionStatus
import textwrap

colors = {'Light':
              {'plots':
                   {'EDA': '#198c53',
                    'DAC': '#18628c',
                    'ACC': '#8c5018'},
               'axis': '#3e3f4f',
               'text': '#000000',
               'button': "#e0e0e0",
               'status': {ConnectionStatus.DISCONNECTED: '#ff5029',
                          ConnectionStatus.CONNECTING: '#ffa500',
                          ConnectionStatus.CONNECTED: '#008c05',
                          ConnectionStatus.ACQUIRING: '#2930ff',
                          ConnectionStatus.ACQUISITION_FINISHED: '#2930ff',
                          ConnectionStatus.CONNECTION_FAILED: '#ff5029'},
               'Windows_fg': "black",
               'Windows_bg': "#F0F0F0"
               },
          'Dark':
              {'plots':
                   {'EDA': '#c9f8d7',
                    'DAC': '#c6eff8',
                    'ACC': '#f8e8c6'},
               'axis': '#ecf1fa',
               'text': '#FFFFFF',
               'button': "#555555",
               'status': {ConnectionStatus.DISCONNECTED: '#f3724f',
                          ConnectionStatus.CONNECTING: '#f8d877',
                          ConnectionStatus.CONNECTED: '#8df877',
                          ConnectionStatus.ACQUIRING: '#77aaf8',
                          ConnectionStatus.CONNECTION_FAILED: '#f3724f',
                          ConnectionStatus.ACQUISITION_FINISHED: '#77aaf8',
                          },
               'Windows_fg': "white",
               'Windows_bg': "#202020"
               }
          }


def open_user_guide(file_path):
    if sys.platform == 'win32':
        os.startfile(file_path)  # For Windows
    elif sys.platform == 'darwin':
        subprocess.run(['open', file_path])  # For macOS
    else:
        subprocess.run(['xdg-open', file_path])  # For Linux


def compute_time_seconds(u_params):
    time_val = None
    if any(duration > 0 for duration in [u_params["duration_h"], u_params["duration_m"],
                                         u_params["duration_s"]]):
        time_val = 0

    if u_params["duration_h"] > 0:
        time_val += u_params["duration_h"] * 3600

    if u_params["duration_m"] > 0:
        time_val += u_params["duration_m"] * 60

    if u_params["duration_s"] > 0:
        time_val += u_params["duration_s"]

    return time_val


def check_time_is_notNull(u_params):
    k_list = ["duration_h", "duration_m", "duration_s"]

    for k_ in k_list:
        if u_params[k_] > 0:
            return True
    return False


def write_params(file_path, params):
    """
    Writes updated parameter values to the parameter file without altering comments or empty lines.

    Args:
        file_path (str): Path to the parameters file.
        params (dict): Dictionary of parameter values to update.
    """

    # Default template to create if file does not exist
    default_template = textwrap.dedent("""\
    # ========================================== User Parameters file ==========================================
    # User parameters. This file contains a list of acquisition parameters which are stored and used before opening.
    # The structure of this file is: <parameter name>=<parameter value>. Please, do not change this structure.
    # If this structure is unreadable, the App will ignore it and use default parameters.
    # Comments under each variable explain their usage.
    # ========================================== Sympathia Connect =============================================
    # © 2024 Sympathia Sense. All rights reserved.
    # This software is protected by copyright laws and international treaties.
    # Unauthorized reproduction, distribution, or use of this software, in whole or in part, is strictly prohibited.
    # All trademarks and registered trademarks are the property of their respective owners.
    # ==========================================================================================================
    
    """)

    explanation = {
    "address": "# address: The communication address for connecting to the ScientISST Sense device.\n# For BTH communication, the address is the BTH MAC address for Linux, serial port address for Mac, or COM port for Windows.",
    "fs": "# fs: The sampling frequency in Hz. Defines how often the data is sampled from the device. Default is 1000 Hz.",
    "ACC_enable": "# ACC_enable: Enables the 1-axial Accelerometer when set to true, and disables it when set to false. Default is false.",
    "EDA_enable": "# EDA_enable: Enables the Electrodermal activity (EDA) Sensor when set to true, and disables it when set to false. Default is false.",
    "duration_h": "# duration_h: The duration hours for data acquisition. The default is 0 hours.",
    "duration_m": "# duration_m: The duration minutes for data acquisition. The default is 1 minute.",
    "duration_s": "# duration_s: The duration seconds for data acquisition. The default is 0 seconds.",
    "verbose": "# verbose: A flag to log sent and received bytes. When set to true, detailed logging of the communication is enabled; otherwise, it is disabled. Default is false.",
    "dac": "# dac: Possibly a specific parameter related to a Digital-to-Analog Converter (DAC) setting. The value 165 could be an identifier or configuration setting for the DAC used in the acquisition system.",
    "auto_load_plot": "# auto_load_plot: Whether to pre-open plot when starting an acquisition, and then closing it at the end. Default is true.",
    "directory": "# directory: Directory path to save files.",
    "naming": "# naming: Naming style. Options: Timestamp, Incremental.",
    "prefix": "# prefix: Prefix.",
    "suffix": "# suffix: Suffix."
    }

    if not os.path.exists(file_path):
        # File doesn't exist, so create it with provided params
        with open(file_path, 'w') as file:
            file.write(default_template)
            for key, value in params.items():
                if isinstance(value, bool):
                    value = "true" if value else "false"
                file.write(f"{key}={value}\n")
                file.write(explanation[key])
                file.write("\n\n")

        return  # Done writing a new file, no need to continue below

        # --- File exists: Read and update only matching keys ---
    updated_lines = []

    with open(file_path, 'r') as file:
        for line in file:
            stripped_line = line.strip()

            # Preserve comments and empty lines
            if not stripped_line or stripped_line.startswith("#"):
                updated_lines.append(line)
                continue

            # Process parameter lines
            if "=" in stripped_line:
                key, value = stripped_line.split("=", 1)
                key = key.strip()

                # Update value if key exists in the dictionary
                if key in params:
                    new_value = params[key]

                    # Ensure booleans are written as lowercase "true" or "false"
                    if isinstance(new_value, bool):
                        new_value = "true" if new_value else "false"

                    # Convert updated value to string and reconstruct the line
                    updated_line = f"{key}={new_value}\n"
                    updated_lines.append(updated_line)
                else:
                    # Keep the original line if the key is not in the dictionary
                    updated_lines.append(line)
            else:
                # Keep the original line (just in case)
                updated_lines.append(line)

    # Write updated lines back to the file
    with open(file_path, 'w') as file:
        file.writelines(updated_lines)


def read_params(file_path):
    """
    Reads parameters from a file and converts them into a dictionary.
    Converts "true" and "false" strings into boolean values.

    Args:
        file_path (str): Path to the parameters file.

    Returns:
        dict: A dictionary of parameter names and their corresponding values.
    """
    params = {}

    with open(file_path, 'r') as file:
        for line in file:
            # Strip leading/trailing whitespace
            line = line.strip()

            # Ignore comments and empty lines
            if line.startswith("#") or not line:
                continue

            # Split into parameter name and value
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                # Attempt to convert value to appropriate type
                if value.lower() == "true":
                    value = True
                elif value.lower() == "false":
                    value = False
                elif value.isdigit():
                    value = int(value)
                else:
                    try:
                        value = float(value)
                    except ValueError:
                        pass  # Leave as string if not int or float

                params[key] = value

    return params


def get_root_project_path(debug=False):
    # If the script is running - 9kph as an executable (e.g., .exe generated by PyInstaller)
    if getattr(sys, 'frozen', False):
        # If the app is frozen (PyInstaller), use sys.executable to find the exe's folder
        root_path = os.path.dirname(sys.executable)
    else:
        # If the script is run as a Python file, use __file__ to get the current script's directory
        root_path = os.path.dirname(os.path.abspath(__file__))

    if debug:
        print("Root folder path: " + root_path)

    return root_path


def get_os_type():
    os_type = platform.system()
    if os_type == "Windows":
        return "Windows"
    elif os_type == "Darwin":  # macOS returns 'Darwin' in platform.system()
        return "MacOS"
    elif os_type == "Linux":
        return "Linux"
    else:
        return "Unknown OS"


def load_icon(rsc_path: str, os_type: str, ld_theme):
    icon_fname = 'icon_dark' if ld_theme == 'Dark' else 'icon_light'
    ext_name = '.icns' if os_type == 'MacOS' else '.ico'

    icon_path = os.path.join(rsc_path, icon_fname + ext_name)

    img = Image.open(icon_path)

    return img


def load_icon_path(rsc_path: str, os_type: str, ld_theme):
    icon_fname = 'icon_dark' if ld_theme == 'Dark' else 'icon_light'
    ext_name = '.icns' if os_type == 'MacOS' else '.ico'

    icon_path = os.path.join(rsc_path, icon_fname + ext_name)

    return icon_path


def closest_division(sample_rate, desired_vieweing_rate):
    decimation_factor = 2  # Start with the smallest integer greater than 1
    vieweing_rate = sample_rate / decimation_factor

    while vieweing_rate > desired_vieweing_rate:
        decimation_factor += 1
        vieweing_rate = sample_rate / decimation_factor

    vieweing_rate = int(vieweing_rate)
    vieweing_period = 1000 * (1 / vieweing_rate)

    return vieweing_rate, vieweing_period, decimation_factor
