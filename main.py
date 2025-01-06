import sys
from tkinter_UI_Windows import App_UI_Windows
from utilities import get_os_type, get_root_project_path
from tkinter_UI_MacOS import App_UI_MacOS
from multiprocessing import freeze_support
from utils.data import create_folder

if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        freeze_support()

    os_type = get_os_type()
    print("Detected operating System: {}".format(os_type))

    create_folder(get_root_project_path(debug=True), "Signals")

    version_number = "1.0.0-beta"
    # comment

    if os_type == 'Windows':
        App_UI_Windows(version=version_number)
    elif os_type == 'MacOS':
        App_UI_MacOS()

