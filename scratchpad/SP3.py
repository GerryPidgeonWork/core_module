import tkinter as tk
from tkinter import ttk

root = tk.Tk()

style = ttk.Style()

print("Default theme:", style.theme_use())

style.configure("My.TButton", background="blue", foreground="black")
ttk.Button(root, text="Test", style="My.TButton").pack(padx=30, pady=30)

root.mainloop()
