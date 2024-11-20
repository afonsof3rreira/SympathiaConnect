import tkinter as tk
import threading

from tkinter_stimuli.file_writer import file_writer


class tkinter_stimuli(tk.Frame):

    def __init__(self, master=None, log_file=None, screen_sz=0.75, lang='portuguese'):
        super().__init__(master)

        self.log_file = log_file

        save_thread = threading.Thread(target=self.log_file.save_timestamps, daemon=True)
        save_thread.start()

        # Create the main window
        self.master = master

        self.master.title("Tkinter Stimuli Experiments")

        # Get screen width and height
        screen_width = round(master.winfo_screenwidth() * screen_sz)
        screen_height = round(master.winfo_screenheight() * screen_sz)

        # Set the window size to full screen but not maximized
        self.master.geometry(f"{screen_width}x{screen_height}")
        self.language = lang

    

if __name__ == '__main__':
    # Create the initial JSON file
    log_file = file_writer()
    log_file.create_initial_file()

    root = tk.Tk()

    app = tkinter_stimuli(master=root, log_file=log_file)
    # app.renew_window()

    app.mainloop()
