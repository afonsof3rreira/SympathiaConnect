import os
import time
import random
import threading
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from file_writer import file_writer
from tkinter_stimuli.aux_functions import T1_movement_seq_gen
from tkinter_stimuli.aux_vars import T1_action_texts, T1_image_paths

class tkinter_stimuli(tk.Frame):

    def __init__(self, master=None, log_file=None):
        super().__init__(master)

        self.log_file = log_file

        save_thread = threading.Thread(target=self.log_file.save_timestamps, daemon=True)
        save_thread.start()

        # Create the main window
        self.master = master

        self.master.title("Renew Window Example")

        # List of image paths (replace with your image paths)
        self.image_paths = T1_image_paths

        self.action_text = T1_action_texts

        # Get screen width and height
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()

        # Set the window size to full screen but not maximized
        self.master.geometry(f"{screen_width}x{screen_height}")

        self.task_text = 'Press Space to perform movement'
        self.progress_bars = None  # Global variable to hold progress bars
        self.progress_active = False  # Flag to track if progress is active
        self.progress_bars = []

        self.action_sequence = T1_movement_seq_gen([0, 1, 2, 3], 4)
        self.action_counter = 0
        self.action_limit = 4 * 4

    def renew_window(self):

        # Destroy all current widgets
        for widget in self.master.winfo_children():
            widget.destroy()

        container_frame = tk.Frame(self.master)
        container_frame.grid(column=0, row=1)

        # Configure row and column weights for centering
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_rowconfigure(1, weight=2)

        self.master.grid_columnconfigure(0, weight=1)

        image = Image.open(self.image_paths["original"])
        image = image.resize((400, 400), Image.LANCZOS)  # Resize the image using LANCZOS algorithm
        photo = ImageTk.PhotoImage(image)

        # create a Label widget
        self.task_label = tk.Label(self.master,
                                   text=self.task_text,
                                   font=("Arial", 25)
                                   )

        self.task_label.grid(column=0, row=0, columnspan=3)

        # Create a label to display the image
        self.image_label = tk.Label(container_frame, image=photo)
        self.image_label.image = photo  # Keep a reference to the image to avoid garbage collection
        self.image_label.grid(column=1, row=1, rowspan=2)

        # Create loading bars in each corner
        self.progress_bars.append(create_loading_bar(container_frame, 0, 1))  # Top-left (left arm; 0)
        self.progress_bars.append(create_loading_bar(container_frame, 0, 2))  # Bottom-left (left leg; 1)
        self.progress_bars.append(create_loading_bar(container_frame, 2, 1))  # Top-right (right arm; 2)
        self.progress_bars.append(create_loading_bar(container_frame, 2, 2))  # Bottom-left (right leg; 3)

        # Bind spacebar press event to update_task_and_progress function
        self.master.bind('<space>', self.update_task_and_progress)

    def update_task_and_progress(self, event):

        if not self.progress_active:
            self.backward_flag = False

            # index is the index of the action counter applied to the action sequence
            idx = self.action_sequence[self.action_counter]

            self.log_file.add_timestamps(self.action_text[idx][0], time.time())

            # this code updates the action text to the first text of the current action, which is lifting the limb
            self.update_action_text(self.action_text[idx][0])

            # update image
            self.update_image(self.image_paths[idx])

            # update bar
            self.animate_progress(self.progress_bars[idx], 0, "forward")

            self.progress_active = True

            self.master.unbind('<space>')  # Disable spacebar while progress is active

    def progress_complete(self):

        self.update_image(self.image_paths["original"])
        self.update_action_text(self.action_text["original"])

        self.task_label.config(text=self.task_text)
        self.progress_active = False

        idx = self.action_sequence[self.action_counter]

        self.log_file.add_timestamps(self.action_text[idx][2], time.time())

        self.action_counter += 1

        # Re-enable space-bar after progress completes
        self.master.bind('<space>', self.update_task_and_progress)

    def update_action_text(self, text_msg):
        self.task_text = text_msg
        self.task_label.config(text=self.task_text)

    def update_image(self, image_path):

        # update image
        image = Image.open(image_path)
        image = image.resize((400, 400), Image.LANCZOS)  # Resize the image using LANCZOS algorithm
        photo = ImageTk.PhotoImage(image)

        self.image_label.config(image=photo)
        self.image_label.image = photo  # Keep a reference to the image to avoid garbage collection

    def animate_progress(self, progress_bar, value, direction):

        if direction == "forward":
            value += 1
            progress_bar["value"] = value
            if value < 100:
                self.master.after(10, lambda: self.animate_progress(progress_bar, value, "forward"))
            else:
                self.animate_progress(progress_bar, value, "backward")

        elif direction == "backward":

            idx = self.action_sequence[self.action_counter]

            if not self.backward_flag:
                # this code updates the action text to the second text of the current action, which is lowering the limb
                self.update_action_text(self.action_text[idx][1])
                self.log_file.add_timestamps(self.action_text[idx][1], time.time())
                self.backward_flag = True

            value -= 1
            progress_bar["value"] = value
            if value > 0:
                self.master.after(10, lambda: self.animate_progress(progress_bar, value, "backward"))
            else:
                self.progress_complete()


def create_loading_bar(parent, col, row):
    # Create a style for the progress bar
    style = ttk.Style()
    style.theme_use('default')  # Use the default theme

    # Configure the style for the progress bar
    style.configure("Custom.Horizontal.TProgressbar", background='red', thickness=30)

    progress = ttk.Progressbar(parent, style="Custom.Horizontal.TProgressbar", orient='vertical', mode='determinate',
                               length=200)
    progress.grid(column=col, row=row)
    return progress


if __name__ == '__main__':
    # Create the initial JSON file
    log_file = file_writer()
    log_file.create_initial_file()

    root = tk.Tk()

    app = tkinter_stimuli(master=root, log_file=log_file)
    app.renew_window()

    app.mainloop()

# Create the "Start" button
# start_button = tk.Button(root, text="Start", command=renew_window, font=('Helvetica', 24))
# start_button.pack(expand=True)

# Start the Tkinter main loop
