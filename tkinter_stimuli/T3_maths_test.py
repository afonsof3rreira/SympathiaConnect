import os
import time
import random
import threading
import tkinter as tk
import numpy as np
from file_writer import file_writer
from tkinter_stimuli.aux_functions import T2_generate_colors, T3_generate_maths_test

"""
Cenários de movimento:

testes com sujeitos:
- estático é o que já temos medido antes
- escrever ao computador (atividade de trabalho de escritório)
- caminhar
- correr

----> utilização de 48 horas numa pessoa

segmentation / artifact detection: deteção de períodos de tempo em que há este ruído / movimentos

"""
class tkinter_stimuli(tk.Frame):

    def __init__(self, master=None, log_file=None, number_of_tests=20, lang='portuguese'):
        """"""

        super().__init__(master)

        self.lang = lang

        if self.lang == 'portuguese':
            pass
        elif self.lang == 'english':
            pass

        self.maths_tests = T3_generate_maths_test(3, [6, 4, 2], np.sum, M=2, digit_order='incremental')

        self.action_limit = len(self.maths_tests)
        print(self.action_limit)

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
        self.master.grid_rowconfigure(2, weight=2)

        self.master.grid_columnconfigure(0, weight=1)

        # Create a Text widget for right option
        self.task_title = tk.Text(self.master,
                                  font=("Arial", 25),
                                  height=1,
                                  bg=self.master.cget("bg"),
                                  bd=0,
                                  highlightthickness=0
                                  )

        if self.lang == 'english':
            task_title_str = "Write the result of the following maths operation and press 'Enter (Return)'"

        elif self.lang == 'portuguese':
            task_title_str = "Escreva o resultado da seguinte operação matemática e pressione 'Enter (Return)'"

        self.task_title.insert("1.0", task_title_str)
        self.task_title.tag_configure("title", justify='center')
        self.task_title.tag_add("title", "1.0", tk.END)
        self.task_title.grid(column=0, row=0)

        self.starting_index = 0

        self.update_curr_math_internal()
        self.first_option_fields()

        self.update_action_text()

        self.action_counter = 0

        self.master.bind('<space>', self.update_math_fields)
        self.master.bind("<Return>", self.key_pressed)


    def key_pressed(self, event):

        key = event.keysym

        print(key)

        # left option is pressed
        try:
            result = int(self.user_answer.get())

        except:
            self.display_error_message()

        if result == self.curr_result:

            # ok, continue, just like when space is pressed
            self.starting_index += 1
            self.update_math_fields(event=True)

        else:
            # display error for half a second
            self.display_error_message()

    def display_error_message(self, ms_time=500):
        # to display the error message we need to temporarily delete the messages and only show a red cross in the middle

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
        self.center_option.grid(column=0, row=1)

        self.master.after(ms_time, lambda: self.update_math_fields(event=True))

    def first_option_fields(self):

        self.update_curr_math_internal()

        # Create a Text widget for left option
        self.center_option = tk.Text(self.master,
                                     font=("Arial", 70),
                                     height=1,
                                     width=20,
                                     bg=self.master.cget("bg"),
                                     bd=0,
                                     highlightthickness=0
                                     )

        math_str = str(self.curr_first_term) + " + " + str(self.curr_second_term)

        self.center_option.insert("1.0", math_str)
        self.center_option.tag_configure("center", justify='center')
        self.center_option.tag_add("center", "1.0", tk.END)

        self.center_option.config(state=tk.DISABLED)
        self.center_option.grid(column=0, row=1)

        vcmd = (root.register(self.validate_input), '%P')

        self.user_answer = tk.StringVar()

        self.entry_answer = tk.Entry(self.master,
                                     font=("Arial", 50),
                                     bg='white',
                                     bd=0,
                                     width=5,
                                     highlightthickness=0,
                                     validate='key',
                                     validatecommand = vcmd,
                                     textvariable=self.user_answer)

        self.entry_answer.grid(column=0, row=2)
        self.entry_answer.focus()

        # self.entry_answer.icursor("1")


    def validate_input(self, new_value):
        # Allow only numeric input
        return new_value.isdigit() or new_value == ""
    def update_curr_math_internal(self):
        self.curr_result = self.maths_tests[self.starting_index][0]
        self.curr_first_term = self.maths_tests[self.starting_index][1]
        self.curr_second_term = self.maths_tests[self.starting_index][2]

    def update_math_fields(self, event):

        if self.starting_index < self.action_limit:
            self.update_curr_math_internal()

            self.center_option.config(state=tk.NORMAL)
            self.center_option.delete("1.0", "end")
            math_str = str(self.curr_first_term) + " + " + str(self.curr_second_term)

            self.center_option.insert(tk.END, math_str)
            self.center_option.tag_configure("center", foreground='black')
            self.center_option.tag_add("center", "1.0", "end")
            self.center_option.config(state=tk.DISABLED)

        # reset
        # self.entry_answer.set("")  # Clear the entry widget
        self.user_answer.set("")

    def update_action_text(self):
        pass

        # # Insert the text
        # self.task_text_widget.insert(tk.END, 'Press the ')
        # self.task_text_widget.insert(tk.END, 'E', ('bold',))
        # self.task_text_widget.insert(tk.END, ' key for ')
        # self.task_text_widget.insert(tk.END, ' and the ')
        # self.task_text_widget.insert(tk.END, 'I', ('bold',))
        # self.task_text_widget.insert(tk.END, ' key for ')
        #
        # # Configure tags for bold text
        # self.task_text_widget.tag_configure('bold', font=("Arial", 20, "bold"), justify='center')
        #
        # # Disable editing
        # self.task_text_widget.config(state=tk.DISABLED)


if __name__ == '__main__':
    # Create the initial JSON file
    log_file = file_writer()
    log_file.create_initial_file()

    root = tk.Tk()

    app = tkinter_stimuli(master=root, log_file=log_file)

    app.mainloop()
