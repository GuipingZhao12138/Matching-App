import tkinter as tk
from tkinter import ttk
import app

# window 
window = tk.Tk()
window.title("Pairfect")
window.geometry('500x800')

#title
title_label = ttk.Label(master = window, text = "Pairfect")
title_label.pack()


# input field
input_frame = ttk.Frame(master = window)
button1 = ttk.Button(master = input_frame, text = "Log in", command = app.login)
button2 = ttk.Button(master = input_frame, text = "Sign up", command = app.create_user)
button1.pack()
button2.pack()
input_frame.pack()

# output 
output_label = ttk.Label(master = window, text = "Output")
output_label.pack(pady = 5)

# run
window.mainloop()

class MatchingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pairfect")
        self.root.geometry("600x500")

        # Set up the database connection
        self.conn = sqlite3.connect('user_profiles.db')
        create_tables(self.conn)

        # Main menu
        self.main_menu()