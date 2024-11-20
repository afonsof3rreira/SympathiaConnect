import os
import time
import random
import threading
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from file_writer import file_writer
from tkinter_stimuli.aux_functions import T2_generate_colors
from tkinter_stimuli.aux_vars import T2_colors_PT, T2_colors_EN


# Congruent option
# if random_number < congruent_rate:

# Function to create pairs of colors and color codes



class tkinter_stimuli(tk.Frame):

    def __init__(self, master=None, log_file=None, number_of_tests=30, mode=1, lang='portuguese'):
        """Mode 0: The meaning of the central word has to be matched with the colored squares on the sides.
           Mode 1: The font color of the central word has to be matched with the colored squares on the sides."""
        super().__init__(master)

        self.mode = mode
        self.lang = lang

        if self.lang == 'portuguese':
            colors = T2_colors_PT
        elif self.lang == 'english':
            colors = T2_colors_EN

        self.color_list = T2_generate_colors(colors, num_tests=number_of_tests)
        print(len(self.color_list))

        self.root_bg_color = root.cget('background')

        self.log_file = log_file

        save_thread = threading.Thread(target=self.log_file.save_timestamps, daemon=True)
        save_thread.start()

        # Create the main window
        self.master = master

        self.master.title("Renew Window Example")

        # Get screen width and height
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()

        # Set the window size to full screen but not maximized
        self.master.geometry(f"{screen_width}x{screen_height}")

        # Configure row and column weights for centering
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_rowconfigure(1, weight=1)
        self.master.grid_rowconfigure(2, weight=1)

        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_columnconfigure(2, weight=1)

        # Create a Text widget for right option
        self.task_title = tk.Text(self.master,
                                  font=("Arial", 25),
                                  height=1,
                                  bg=self.master.cget("bg"),
                                  bd=0,
                                  highlightthickness=0
                                  )

        if self.lang == 'english':
            if mode == 0:
                task_title_str = "Select the square that matches the semantic meaning of the word at the center."

            if mode == 1:
                task_title_str = "Select the square that matches the font color of the word at the center."

        elif self.lang == 'portuguese':
            if mode == 0:
                task_title_str = "Escolha o quadrado correspondente ao significado semântico da palavra no centro."

            if mode == 1:
                task_title_str = "Escolha o quadrado correspondente à cor da letra da palavra no centro."

        self.task_title.insert("1.0", task_title_str)
        self.task_title.tag_configure("title", justify='center')
        self.task_title.tag_add("title", "1.0", tk.END)
        self.task_title.grid(column=0, row=0, columnspan=3)

        self.starting_index = 0

        self.update_color_options()

        self.first_option_fields()

        # Create a Text widget with a transparent background
        self.task_text_widget = tk.Text(self.master,
                                        font=("Arial", 20),
                                        height=2,
                                        bg=self.master.cget("bg"),
                                        bd=0,
                                        highlightthickness=0)

        self.task_text_widget.grid(column=0, row=2, columnspan=3)

        self.update_action_text()

        self.action_counter = 0
        self.action_limit = number_of_tests

        self.master.bind('<space>', self.update_options_fields)

        # Bind key events
        self.master.bind('<i>', self.key_pressed)
        self.master.bind('<e>', self.key_pressed)

    def key_pressed(self, event):

        key = event.keysym

        if key == 'e':
            print("left pressed")

            # left option is pressed
            if self.correct_option == "left":
                # ok, continue, just like when space is pressed
                self.starting_index += 1
                self.update_options_fields(event=True)

            else:
                # display error for half a second
                self.display_error_message()

        elif key == 'i':
            # right option is pressed

            # right option is pressed
            if self.correct_option == "right":
                # ok, continue, just like when space is pressed
                self.starting_index += 1
                self.update_options_fields(event=True)

            else:
                # display error for half a second
                self.display_error_message(ms_time=500)


    def display_error_message(self, ms_time=500):
        # to display the error message we need to temporarily delete the messages and only show a red cross in the middle

        self.left_option = tk.Frame(self.master, bg=self.root_bg_color, width=100, height=100, padx=3, pady=3)
        self.left_option.grid(column=0, row=1, sticky="e")

        self.right_option = tk.Frame(self.master, bg=self.root_bg_color, width=100, height=100, padx=3, pady=3)
        self.right_option.grid(column=2, row=1, sticky="w")

        # Create a Text widget for left option
        self.center_option = tk.Text(self.master,
                                     font=("Arial", 70),
                                     height=1,
                                     width=20,
                                     bg=self.master.cget("bg"),
                                     bd=0,
                                     highlightthickness=0
                                     )

        self.center_option.insert("1.0", "×")
        self.center_option.tag_configure("center", justify='center', foreground='red')
        self.center_option.tag_add("center", "1.0", tk.END)

        self.center_option.config(state=tk.DISABLED)
        self.center_option.grid(column=1, row=1)

        self.master.after(ms_time, lambda: self.update_options_fields(event=True))

    def first_option_fields(self):

        self.update_color_options()

        # Create a Text widget for left option
        self.left_option = tk.Frame(self.master, bg=self.left_option_text, width=100, height=100, padx=3, pady=3)
        self.left_option.grid(column=0, row=1, sticky="e")

        # self.left_option = tk.Text(self.master,
        #                            font=("Arial", 40),
        #                            height=1,
        #                            width=20,
        #                            bg=self.master.cget("bg"),
        #                            bd=0,
        #                            highlightthickness=0
        #                            )
        #
        # self.left_option.insert(tk.END, self.left_option_text)
        # self.left_option.tag_configure("center", justify='right')
        # self.left_option.tag_add("center", "1.0", "end")
        # self.left_option.config(state=tk.DISABLED)
        # self.left_option.grid(column=0, row=1)

        # Create a Text widget for right option
        self.right_option = tk.Frame(self.master, bg=self.right_option_text, width=100, height=100, padx=3, pady=3)
        self.right_option.grid(column=2, row=1, sticky="w")

        # self.right_option = tk.Text(self.master,
        #                             font=("Arial", 40),
        #                             height=1,
        #                             width=20,
        #                             bg=self.master.cget("bg"),
        #                             bd=0,
        #                             highlightthickness=0
        #                             )
        # self.right_option.insert(tk.END, self.right_option_text)
        # self.right_option.tag_configure("center", justify='left')
        # self.right_option.tag_add("center", "1.0", "end")
        # self.right_option.config(state=tk.DISABLED)
        # self.right_option.grid(column=2, row=1)

        # Create a Text widget for left option
        self.center_option = tk.Text(self.master,
                                     font=("Arial", 70),
                                     height=1,
                                     width=20,
                                     bg=self.master.cget("bg"),
                                     bd=0,
                                     highlightthickness=0
                                     )
        self.center_option.insert("1.0", self.current_testing_text)
        self.center_option.tag_configure("center", justify='center', foreground=self.current_testing_color)
        self.center_option.tag_add("center", "1.0", tk.END)

        self.center_option.config(state=tk.DISABLED)
        self.center_option.grid(column=1, row=1)

    def update_color_options(self):
        """Congruent rate refers to the likelihood that a congruent option will be displayed."""

        congruent = self.color_list[self.starting_index][2]
        side_allocation = self.color_list[self.starting_index][3]  # 0 = original to left, 1 = original to right

        if self.mode == 0:
            correct_index = 0
        elif self.mode == 1:
            correct_index = 1

        # Congruent option
        if congruent:
            # the color of the word matches the meaning of the word
            self.current_testing_text = self.color_list[self.starting_index][0][0]
            self.current_testing_color = self.color_list[self.starting_index][0][1]

        # Incongruent option
        else:
            # the color of the word does not match the meaning of the word
            self.current_testing_text = self.color_list[self.starting_index][0][0]
            self.current_testing_color = self.color_list[self.starting_index][1][1]

        if side_allocation == 0:
            self.left_option_text = self.color_list[self.starting_index][0][1]
            self.right_option_text = self.color_list[self.starting_index][1][1]

            if self.mode == 0:
                self.correct_option = "left"

            elif self.mode == 1 and not congruent:
                self.correct_option = "right"

        elif side_allocation == 1:

            # two options, one being the
            self.left_option_text = self.color_list[self.starting_index][1][1]
            self.right_option_text = self.color_list[self.starting_index][0][1]

            if self.mode == 0:
                self.correct_option = "right"

            elif self.mode == 1 and not congruent:
                self.correct_option = "left"

    def update_options_fields(self, event):

        if self.starting_index < self.action_limit:
            self.update_color_options()

            # Clear previous text and insert updated text
            self.right_option.configure(bg=self.right_option_text)

            # self.right_option.config(state=tk.NORMAL)
            # self.right_option.delete("1.0", tk.END)
            # self.right_option.insert(tk.END, self.right_option_text)
            # self.right_option.tag_configure("center", justify='left')
            # self.right_option.tag_add("center", "1.0", "end")
            # self.right_option.config(state=tk.DISABLED)

            # Clear previous text and insert updated text
            self.left_option.configure(bg=self.left_option_text)

            # self.left_option.config(state=tk.NORMAL)
            # self.left_option.delete("1.0", tk.END)
            # self.left_option.insert(tk.END, self.left_option_text)
            # self.left_option.tag_configure("center", justify='right')
            # self.left_option.tag_add("center", "1.0", "end")
            # self.left_option.config(state=tk.DISABLED)

            self.center_option.config(state=tk.NORMAL)
            self.center_option.delete("1.0", "end")
            self.center_option.insert(tk.END, self.current_testing_text)
            self.center_option.tag_configure("center", foreground=self.current_testing_color)
            self.center_option.tag_add("center", "1.0", "end")
            self.center_option.config(state=tk.DISABLED)

    def update_action_text(self):

        # Insert the text
        if self.lang == 'english':
            self.task_text_widget.insert(tk.END, 'Press the ')
            self.task_text_widget.insert(tk.END, 'E', ('bold',))
            self.task_text_widget.insert(tk.END, ' key for left option')
            self.task_text_widget.insert(tk.END, ' and the ')
            self.task_text_widget.insert(tk.END, 'I', ('bold',))
            self.task_text_widget.insert(tk.END, ' key for right option')

        elif self.lang == 'portuguese':
            self.task_text_widget.insert(tk.END, 'Pressione na tecla ')
            self.task_text_widget.insert(tk.END, 'E', ('bold',))
            self.task_text_widget.insert(tk.END, ' para a opção à esquerda')
            self.task_text_widget.insert(tk.END, ' e a tecla ')
            self.task_text_widget.insert(tk.END, 'I', ('bold',))
            self.task_text_widget.insert(tk.END, ' para a opção à direita')


        # Configure tags for bold text
        self.task_text_widget.tag_configure('task_text_widget', justify='center')
        self.task_text_widget.tag_add('task_text_widget', "1.0", tk.END)


        # Disable editing
        self.task_text_widget.config(state=tk.DISABLED)

    def renew_window(self):
        pass

        # Bind spacebar press event to update_task_and_progress function
        # self.master.bind('<space>', self.update_task_and_progress)


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
