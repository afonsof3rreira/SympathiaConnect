import inspect
import os
from utilities import get_os_type
from tkinter_UI import App_UI

if __name__ == "__main__":


    os_type = get_os_type()
    print("Detected operating System: {}".format(os_type))

    App_UI(os_type=os_type)
    # functions to be run
