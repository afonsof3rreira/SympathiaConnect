import tkinter as tk
import threading

from tkinter_stimuli.aux_vars import T0_texts
from tkinter_stimuli.file_writer import file_writer


class tkinter_stimuli(tk.Frame):
    """
    ---- Page 0: subject ID to be filled and validated by the helper ----

    row 0, col 0: Screen Title: "Subject Info Screen"
    row 1, col 0: Subtitle: "Subject Code", col 1: Entry for "Subject Code"

    bottom, right: "Next"

    ---- Page 1: Anthropometric info to be filled by the subject ----

    row 2, col 0: Subtitle: "Age group"
    row 3: col 0: Checkbox for "Age group". Options: 18-29, 30-39, 40-49, 50-59, 60-69, 70-79, >80

    row 4, col 0: Subtitle: "Sex", col 1: ??
    row 5, col 0: Checkbox for "Sex". Options: Male, Female, Other, Prefer not to say

    row 6, col 0: Subtitle: "Height", col 1: Entry for "Height", col 2: Checkbox for unit for height. Options: Centimeters (cm), Inches (")
    row 7, col 0: Subtitle: "Weight", col 1: Entry for "Weight", col 2: Checkbox for unit for weight. Options: Kilogram (kg), Pound (lb)
    row 8, col 0: Subtitle: "Foot / shoe size", col 1: Entry for "Foot / shoe size", col 2: Checkbox for unit of foot size (EU, US, UK, ...?)

    bottom, left: "Previous", right: "Next"

    ---- Page 1: Ankle measurement to be measured and filled by the subject with the help of the helper----

    row 9, col 0: Subtitle: "Ankle Perimeter", col 1: Entry for "Ankle Perimeter", col 2: Unit for ankle perimeter, Centimeter (Cm)

    bottom, left: "Previous", right: "Validate answers"

    """

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

        if lang == 'english':
            self.lang = 'en'
        elif lang == 'portuguese':
            self.lang = 'pt'
        else:
            raise ValueError("Language {} not supported".format(lang))

        # Configure row and column weights for centering
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_rowconfigure(1, weight=1)
        self.master.grid_rowconfigure(2, weight=2)

        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)

        self.current_screen = 1

        # User input variables
        self.user_ID = tk.StringVar()
        self.age_var_1 = tk.BooleanVar()
        self.age_var_2 = tk.BooleanVar()
        self.age_var_3 = tk.BooleanVar()
        self.age_var_4 = tk.BooleanVar()
        self.age_var_5 = tk.BooleanVar()
        self.sex_var_1 = tk.BooleanVar()
        self.sex_var_2 = tk.BooleanVar()
        self.sex_var_3 = tk.BooleanVar()
        self.sex_var_4 = tk.BooleanVar()
        self.height = tk.StringVar()
        self.weight = tk.StringVar()
        self.shoe_size = tk.StringVar()
        self.ankle_perimeter = tk.StringVar()

        self.screen_1()

    def screen_1(self):
        """
        row 0, col 0: Screen Title: "Subject Info Screen"
        row 1, col 0: Subtitle: "Subject Code", col 1: Entry for "Subject Code"
        """

        # create a Label widget
        self.title = tk.Label(self.master,
                              text=T0_texts['screen 1']['title'][self.lang],
                              font=("Arial", 30)
                              )

        self.title.grid(row=0, column=0, columnspan=2)

        # create a Label widget
        self.subtitle_1 = tk.Label(self.master,
                                   text=T0_texts['screen 1']['subtitle 1'][self.lang],
                                   font=("Arial", 20)
                                   )

        self.subtitle_1.grid(row=1, column=0, columnspan=1)

        vcmd = (self.master.register(self.validate_user_ID), '%P')

        self.option_1 = tk.Entry(self.master,
                                 font=("Arial", 50),
                                 bg='white',
                                 bd=0,
                                 width=5,
                                 highlightthickness=0,
                                 validate='key',
                                 validatecommand=vcmd,
                                 textvariable=self.user_ID)

        self.option_1.grid(row=1, column=1, columnspan=2, sticky='w')
        self.option_1.focus()

        self.next_button = tk.Button(self.master, text="Next", command=self.next_screen, width=10, height=2, font=("Helvetica", 20))
        self.next_button.grid(row=2, column=1, sticky='se')
        self.next_button.config(state="disabled")

        self.user_ID.trace_add("write", self.update_next_button_state)

    def show_screen_2(self):
        """
        row 2, col 0: Subtitle: "Age group"
        row 3: col 0: Checkbox for "Age group". Options: 18-29, 30-39, 40-49, 50-59, 60-69, 70-79, >80

        row 4, col 0: Subtitle: "Sex", col 1: ??
        row 5, col 0: Checkbox for "Sex". Options: Male, Female, Other, Prefer not to say

        row 6, col 0: Subtitle: "Height", col 1: Entry for "Height", col 2: Checkbox for unit for height. Options: Centimeters (cm), Inches (")
        row 7, col 0: Subtitle: "Weight", col 1: Entry for "Weight", col 2: Checkbox for unit for weight. Options: Kilogram (kg), Pound (lb)
        row 8, col 0: Subtitle: "Foot / shoe size", col 1: Entry for "Foot / shoe size", col 2: Checkbox for unit of foot size (EU, US, UK, ...?)
        """

        # Configure row and column weights for centering
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_rowconfigure(1, weight=1)
        self.master.grid_rowconfigure(2, weight=2)
        self.master.grid_rowconfigure(3, weight=2)
        self.master.grid_rowconfigure(4, weight=2)
        self.master.grid_rowconfigure(5, weight=2)
        self.master.grid_rowconfigure(6, weight=2)


        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_columnconfigure(2, weight=1)
        self.master.grid_columnconfigure(3, weight=1)

        # create a Label widget
        self.title = tk.Label(self.master,
                              text=T0_texts['screen 2']['title'][self.lang],
                              font=("Arial", 30)
                              )

        self.title.grid(row=0, column=0, columnspan=4)

        # create a Label widget
        self.subtitle_1 = tk.Label(self.master,
                                   text=T0_texts['screen 2']['subtitle 1'][self.lang],
                                   font=("Arial", 30)
                                   )

        self.subtitle_1.grid(row=1, column=0, columnspan=4)

        self.container_options = tk.Frame(self.master)
        self.container_options.grid(row=2, column=0, columnspan=4)



        self.age_vars = [self.age_var_1, self.age_var_2, self.age_var_3, self.age_var_4, self.age_var_5]
        self.option_btns = []

        for i in range(5):
            self.option_btns.append(tk.Checkbutton(self.container_options,
                                       text=T0_texts['screen 2']['options 1'][self.lang][i],
                                       font=("Arial", 20),
                                       bg=self.master.cget('bg'),
                                       width=7,
                                       highlightthickness=0,
                                       variable=self.age_vars[i],
                                       offvalue=False,
                                       command=self.update_btn_states_1,
                                       )
                                    )
            self.option_btns[i].pack(side='left', padx=2)


        self.subtitle_2 = tk.Label(self.master,
                                   text=T0_texts['screen 2']['subtitle 2'][self.lang],
                                   font=("Arial", 30),
                                   )

        self.subtitle_2.grid(row=3, column=0, columnspan=4)


        self.container_options_2 = tk.Frame(self.master)
        self.container_options_2.grid(row=4, column=0, columnspan=4)

        self.sex_vars = [self.sex_var_1, self.sex_var_2, self.sex_var_3, self.sex_var_4]
        self.option_btns_2 = []

        for i in range(4):
            self.option_btns_2.append(tk.Checkbutton(self.container_options_2,
                                       text=T0_texts['screen 2']['options 2'][self.lang][i],
                                       font=("Arial", 20),
                                       bg=self.master.cget('bg'),
                                       width=15,
                                       highlightthickness=0,
                                       variable=self.sex_vars[i],
                                       offvalue=False,
                                       command=self.update_btn_states_2,
                                       )
                                    )

            self.option_btns_2[i].pack(side='left', padx=2)

        # create a Label widget
        self.subtitle_3 = tk.Label(self.master,
                                   text=T0_texts['screen 2']['subtitle 3'][self.lang],
                                   font=("Arial", 30)
                                   )

        self.subtitle_3.grid(row=5, column=0)

        vcmd = (self.master.register(self.validate_height_weight), '%P')

        self.entry_3 = tk.Entry(self.master,
                                 font=("Arial", 30),
                                 bg='white',
                                 bd=0,
                                 width=5,
                                 highlightthickness=0,
                                 validate='key',
                                 validatecommand=vcmd,
                                 textvariable=self.height)

        self.entry_3.grid(row=5, column=1)

        self.var_height_unit_cm = tk.BooleanVar()
        self.var_height_unit_pol = tk.BooleanVar()

        self.btn_height_unit_cm = tk.Checkbutton(self.master,
                                                 text=T0_texts['screen 2']['options 3'][self.lang][0],
                                                 font=("Arial", 20),
                                                 bg=self.master.cget('bg'),
                                                 width=15,
                                                 highlightthickness=0,
                                                 variable=self.var_height_unit_cm,
                                                 offvalue=False,
                                                 command=self.update_btn_height,
                                                 )

        self.btn_height_unit_cm.grid(row=5, column=2)

        self.btn_height_unit_pol = tk.Checkbutton(self.master,
                                                 text=T0_texts['screen 2']['options 3'][self.lang][1],
                                                 font=("Arial", 20),
                                                 bg=self.master.cget('bg'),
                                                 width=15,
                                                 highlightthickness=0,
                                                 variable=self.var_height_unit_pol,
                                                 offvalue=False,
                                                 command=self.update_btn_height,
                                                 )

        self.btn_height_unit_pol.grid(row=5, column=3)


        self.var_weight_unit_kg = tk.BooleanVar()
        self.var_weight_unit_lb = tk.BooleanVar()

        # create a Label widget
        self.subtitle_4 = tk.Label(self.master,
                                   text=T0_texts['screen 2']['subtitle 4'][self.lang],
                                   font=("Arial", 30)
                                   )

        self.subtitle_4.grid(row=6, column=0)

        vcmd = (self.master.register(self.validate_height_weight), '%P')

        self.entry_4 = tk.Entry(self.master,
                                 font=("Arial", 30),
                                 bg='white',
                                 bd=0,
                                 width=5,
                                 highlightthickness=0,
                                 validate='key',
                                 validatecommand=vcmd,
                                 textvariable=self.weight)

        self.entry_4.grid(row=6, column=1)

        self.btn_weight_unit_kg = tk.Checkbutton(self.master,
                                                 text=T0_texts['screen 2']['options 4'][self.lang][0],
                                                 font=("Arial", 20),
                                                 bg=self.master.cget('bg'),
                                                 width=15,
                                                 highlightthickness=0,
                                                 variable=self.var_weight_unit_kg,
                                                 offvalue=False,
                                                 command=self.update_btn_weight,
                                                 )

        self.btn_weight_unit_kg.grid(row=6, column=2)

        self.btn_weight_unit_lb = tk.Checkbutton(self.master,
                                                 text=T0_texts['screen 2']['options 4'][self.lang][1],
                                                 font=("Arial", 20),
                                                 bg=self.master.cget('bg'),
                                                 width=15,
                                                 highlightthickness=0,
                                                 variable=self.var_weight_unit_lb,
                                                 offvalue=False,
                                                 command=self.update_btn_weight,
                                                 )

        self.btn_weight_unit_lb.grid(row=6, column=3)

        self.next_button = tk.Button(self.master, text="Next", command=self.next_screen, width=10, height=2, font=("Helvetica", 20))
        self.next_button.grid(row=7, column=3, sticky='se')
        self.next_button.config(state="disabled")

        for age_var in self.age_vars:
            age_var.trace_add("write", self.update_next_button_state)

        for sex_var in self.sex_vars:
            sex_var.trace_add("write", self.update_next_button_state)

        self.var_height_unit_cm.trace_add("write", self.update_next_button_state)
        self.var_height_unit_pol.trace_add("write", self.update_next_button_state)

        self.var_weight_unit_kg.trace_add("write", self.update_next_button_state)
        self.var_weight_unit_lb.trace_add("write", self.update_next_button_state)
        self.height.trace_add("write", self.update_next_button_state)

        self.weight.trace_add("write", self.update_next_button_state)

    def update_btn_weight(self):

        if not self.var_weight_unit_kg.get() and not self.var_weight_unit_lb.get():
            self.btn_weight_unit_kg.config(state='active')
            self.btn_weight_unit_lb.config(state='active')

        elif self.var_weight_unit_kg.get() and not self.var_weight_unit_lb.get():
            self.btn_weight_unit_lb.config(state='disabled')
            self.btn_weight_unit_kg.config(state='active')

        elif not self.var_weight_unit_kg.get() and self.var_weight_unit_lb.get():
            self.btn_weight_unit_lb.config(state='active')
            self.btn_weight_unit_kg.config(state='disabled')

    def update_btn_height(self):

        if not self.var_height_unit_cm.get() and not self.var_height_unit_pol.get():
            self.btn_height_unit_cm.config(state='active')
            self.btn_height_unit_pol.config(state='active')

        elif self.var_height_unit_cm.get() and not self.var_height_unit_pol.get():
            self.btn_height_unit_pol.config(state='disabled')
            self.btn_height_unit_cm.config(state='active')

        elif not self.var_height_unit_cm.get() and self.var_height_unit_pol.get():
            self.btn_height_unit_pol.config(state='active')
            self.btn_height_unit_cm.config(state='disabled')

    def update_btn_states_1(self):

        activated_btn_idx = None

        for i in range(5):
            if self.age_vars[i].get():
                activated_btn_idx = i

        if activated_btn_idx is not None:
            for i in range(5):
                if i != activated_btn_idx:
                    self.option_btns[i].config(state='disabled')
        else:
            for i in range(5):
                try:
                    self.option_btns[i].config(state='active')
                except:
                    pass

    def update_btn_states_2(self):

        activated_btn_idx = None

        for i in range(4):
            print(self.sex_vars[i].get())
            if self.sex_vars[i].get():
                activated_btn_idx = i

        if activated_btn_idx is not None:
            for i in range(4):
                if i != activated_btn_idx:
                    self.option_btns_2[i].config(state='disabled')
        else:
            for i in range(4):
                try:
                    self.option_btns_2[i].config(state='active')
                except:
                    pass

    def rmv_screen_1(self):

        self.title.grid_forget()
        self.title.grid_remove()

        self.subtitle_1.grid_forget()
        self.subtitle_1.grid_remove()

        self.option_1.grid_forget()
        self.option_1.grid_remove()

        self.next_button.grid_forget()
        self.next_button.grid_remove()

    def next_screen(self):
        print(self.current_screen)

        if self.current_screen == 1:
            # self.show_screen_2()
            self.rmv_screen_1()
            self.show_screen_2()

            # store user_ID
            self.log_file.add_user_ID(self.user_ID.get())

            self.current_screen += 1

        elif self.current_screen == 2:
            # self.screen_2()
            print(self.age_vars[0].get())

            # store user_ID
            anthropometric_data = self.data_processor()
            self.log_file.add_user_anthropometric_data(anthropometric_data)

            pass
        elif self.current_screen == 3:
            # self.screen_3()
            pass

    def data_processor(self):
        anthropometric_data = {}

        # age group
        for i in range(len(self.age_vars)):
            if self.age_vars[i].get():
                anthropometric_data["age_group"] = T0_texts["screen 2"]["options 1"]["en"][i]

        # sex
        for i in range(len(self.sex_vars)):
            if self.sex_vars[i].get():
                anthropometric_data["sex"] = T0_texts["screen 2"]["options 2"]["en"][i]

        # height value
        anthropometric_data["height"] = self.height.get()

        # height unit
        if self.var_height_unit_cm.get():
            anthropometric_data["height_unit"] = T0_texts["screen 2"]["options 3"]["en"][0]
        else:
            anthropometric_data["height_unit"] = T0_texts["screen 2"]["options 3"]["en"][1]

        # weight value
        anthropometric_data["weight"] = self.weight.get()

        # weight unit
        if self.var_weight_unit_kg.get():
            anthropometric_data["weight_unit"] = T0_texts["screen 2"]["options 4"]["en"][0]
        else:
            anthropometric_data["weight_unit"] = T0_texts["screen 2"]["options 4"]["en"][1]

        return anthropometric_data

    def update_next_button_state(self, *args):
        """method to update the state of the next button"""
        if self.current_screen == 1:
            entry_value = self.user_ID.get()
            if len(entry_value) == 5:
                self.next_button.config(state='normal')
            else:
                self.next_button.config(state='disabled')

        elif self.current_screen == 2:

            screen_filled = False
            for age_var in self.age_vars:
                if age_var.get():
                    screen_filled = True
                    break

            if screen_filled:
                screen_filled = False
                for sex_var in self.sex_vars:
                    if sex_var.get():
                        screen_filled = True
                        break

            if screen_filled:
                screen_filled = False
                if 2 <= len(self.height.get()) <= 3:
                    screen_filled = True

            if screen_filled:
                screen_filled = False
                if self.var_height_unit_cm.get() or self.var_height_unit_pol.get():
                    screen_filled = True

            if screen_filled:
                screen_filled = False
                if 2 <= len(self.weight.get()) <= 3:
                    screen_filled = True

            if screen_filled:
                screen_filled = False
                if self.var_weight_unit_kg.get() or self.var_weight_unit_lb.get():
                    screen_filled = True

            if screen_filled:
                self.next_button.config(state='normal')
            else:
                self.next_button.config(state='disabled')

    def validate_user_ID(self, new_value):
        # Allow only numeric input
        if (new_value.isdigit() and len(new_value) < 6) or new_value == "":
            return True
        else:
            return False

    def validate_height_weight(self, new_value):
        # Allow only numeric input
        if (new_value.isdigit() and len(new_value) < 4) or new_value == "":
            return True
        else:
            return False

if __name__ == '__main__':
    # Create the initial JSON file
    log_file = file_writer()
    log_file.create_initial_file()

    root = tk.Tk()

    app = tkinter_stimuli(master=root, log_file=log_file)

    app.mainloop()
