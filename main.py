from tkinter_UI_Windows import App_UI_Windows
from utilities import get_os_type
from tkinter_UI_MacOS import App_UI_MacOS

if __name__ == "__main__":

    os_type = get_os_type()
    print("Detected operating System: {}".format(os_type))

    if os_type == 'Windows':
        App_UI_Windows()
    elif os_type == 'MacOS':
        App_UI_MacOS()