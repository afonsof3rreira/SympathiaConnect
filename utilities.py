import platform
from PIL import Image
import os
import sys
import subprocess
import sys
from utils.bluetooth_MacOS import ConnectionStatus

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
                          ConnectionStatus.ACQUIRING: '#2930ff'},
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
                     ConnectionStatus.ACQUIRING: '#77aaf8'
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

def write_params(file_path, params):
    """
    Writes updated parameter values to the parameter file without altering comments or empty lines.

    Args:
        file_path (str): Path to the parameters file.
        params (dict): Dictionary of parameter values to update.
    """
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
    # If the script is running as an executable (e.g., .exe generated by PyInstaller)
    if getattr(sys, 'frozen', False):
        # Get the temporary folder where the executable was unpacked
        root_path = sys._MEIPASS
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

    print(icon_path)

    img = Image.open(icon_path)

    return img


def closest_division(sample_rate, desired_vieweing_rate):
    decimation_factor = 2  # Start with the smallest integer greater than 1
    vieweing_rate = sample_rate / decimation_factor

    while vieweing_rate > desired_vieweing_rate:
        decimation_factor += 1
        vieweing_rate = sample_rate / decimation_factor

    vieweing_rate = int(vieweing_rate)
    vieweing_period = 1000 * (1 / vieweing_rate)

    return vieweing_rate, vieweing_period, decimation_factor
