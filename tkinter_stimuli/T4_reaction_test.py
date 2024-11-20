import tkinter as tk
import random
import time

class ReactionTest:
    def __init__(self, root):
        self.root = root
        self.root.title("Speed Reaction Test")

        self.label = tk.Label(root, text="Wait for the square to turn red and then press the space bar!", font=('Helvetica', 16))
        self.label.pack(pady=20)

        self.canvas = tk.Canvas(root, width=200, height=200)
        self.canvas.pack(pady=20)

        self.square = self.canvas.create_rectangle(50, 50, 150, 150, fill="SystemButtonFace")

        self.button = tk.Button(root, text="Start", font=('Helvetica', 16), command=self.start_test)
        self.button.pack(pady=20)

        self.root.bind('<space>', self.space_press)

        self.start_time = 0
        self.waiting_for_click = False

    def start_test(self):
        self.label.config(text="Wait for it...")
        self.button.config(state="disabled")
        self.canvas.itemconfig(self.square, fill="SystemButtonFace")
        delay = random.randint(1000, 5000)  # Random delay between 1 and 5 seconds
        self.root.after(delay, self.change_color)

    def change_color(self):
        self.canvas.itemconfig(self.square, fill="red")
        self.start_time = time.time()
        self.waiting_for_click = True

    def space_press(self, event):
        if self.waiting_for_click:
            reaction_time = time.time() - self.start_time
            self.label.config(text=f"Your reaction time is {reaction_time:.3f} seconds")
            self.button.config(text="Start Again", state="normal")
            self.waiting_for_click = False
        else:
            self.label.config(text="Wait for the square to turn red and then press the space bar!")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = ReactionTest(root)
    app.run()
