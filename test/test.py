import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("初めてのTkinter")

label=ttk.Label(root,
                text="あいうえお",
                foreground="#FFFFFF",
                padding=(0,5),
                font=("Times New Roman",20)
                )


entry1=ttk.Entry(root)
entry2=ttk.Entry(root,show="●")
button=ttk.Button(root,text="OK")

label.pack()
entry1.pack()
entry2.pack()
button.pack()

root.mainloop()