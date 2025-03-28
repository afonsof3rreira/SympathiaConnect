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
    try:
        app = None

        if os_type == 'Windows':
            app = App_UI_Windows(version=version_number)
        elif os_type == 'MacOS':
            app = App_UI_MacOS()

        app.get_app().mainloop()


    except KeyboardInterrupt:
        print("KeyboardInterrupt detected! Cleaning up before exiting...")


    except Exception as e:
        print(f"An unexpected error occurred: {e}")  # Debug other issues


    finally:

        if app is not None:

            app.cleanup()  # Ensure cleanup runs
            print("Clean up executed.")

            print("Application closed.")

        sys.exit(0)  # Exit safely
