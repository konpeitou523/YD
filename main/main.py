import tkinter as tk
from tkinter import Tk, StringVar
from tkinter import filedialog
from tkinter import ttk

root = Tk()
root.title("YouTube Downloader")
root.geometry("800x300")

standard_font="Times New Roman"

frame_1=tk.Frame(root)
label_1=ttk.Label(frame_1,
                text="YouTubeのリンクを入力",
                foreground="#FFFFFF",
                font=(standard_font,12),
                padding=(0,0))

frame_2=tk.Frame(root)
text_1=tk.Text(frame_2,wrap="char",height=3)

frame_3=tk.Frame(root)
frame_3_1=tk.Frame(frame_3)
label_2=ttk.Label(frame_3_1,
                text="画質を選択",
                foreground="#FFFFFF",
                font=(standard_font,12),
                padding=(0,0))
quality_option=StringVar()
combo1=ttk.Combobox(frame_3_1,textvariable=quality_option,values=["144p","240p","360p","480p","720p","1080p"])
combo1.current(2)
frame_3_2=tk.Frame(frame_3)
label_3=ttk.Label(frame_3_2,
                text="フォーマットを選択",
                foreground="#FFFFFF",
                font=(standard_font,12),
                padding=(0,0))
format_option=StringVar()
combo2=ttk.Combobox(frame_3_2,textvariable=format_option,values=["mp4","mp3","wav"])
combo2.current(0)

frame_4=tk.Frame(root)
label_4=ttk.Label(frame_4,
                  text="保存先:",
                  foreground="#FFFFFF",
                  font=(standard_font,12),
                  padding=(0,0))
entry_1=ttk.Entry(frame_4,state="readonly")
button_1=ttk.Button(frame_4,text="参照",command=lambda:select_folder(entry_1))
def select_folder(entry_widget):
    folder_path = filedialog.askdirectory()
    if folder_path:  # キャンセルされなければ
        entry_widget.config(state="normal")
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, folder_path)
        entry_widget.config(state="readonly")

frame_5=tk.Frame(root)
button_2=ttk.Button(frame_5,text="現在の設定を保存")
button_3=ttk.Button(frame_5,text="オプション")
button_4=ttk.Button(frame_5,text="ダウンロード開始")



frame_1.pack(fill="x",padx=10,pady=2)
label_1.pack(side="left")

frame_2.pack(fill="x",padx=3,pady=2)
text_1.pack(fill="x")

frame_3.pack(fill="x",padx=10,pady=2)
frame_3_1.pack(side="left", fill="both", expand=True)
label_2.pack(side="left",anchor="w", padx=5, pady=5)
combo1.pack(side="left",anchor="w",padx=5)
frame_3_2.pack(side="left", fill="both", expand=True)
label_3.pack(side="left",anchor="w", padx=5, pady=5)
combo2.pack(side="left",anchor="w",padx=5)

frame_4.pack(fill="x",padx=10,pady=2)
frame_4.columnconfigure(1,weight=1)
label_4.grid(row=0,column=0)
entry_1.grid(row=0,column=1,sticky="ew",padx=5)
button_1.grid(row=0,column=2)

frame_5.pack(fill="x",padx=10,pady=2,side="bottom")
frame_5.columnconfigure(0,weight=1)
button_2.grid(row=0,column=1,padx=5)
button_3.grid(row=0,column=2,padx=5)
button_4.grid(row=0,column=3,padx=5)

root.mainloop()