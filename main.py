import os
import sys
import subprocess
import tkinter as tk
from tkinter import Tk, StringVar
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
import yt_dlp

if sys.platform == "win32":
    ffmpeg_path = os.path.join(os.path.dirname(__file__), "ffmpeg", "ffmpeg.exe")
elif sys.platform == "darwin":
    ffmpeg_path = os.path.join(os.path.dirname(__file__), "ffmpeg","ffmpeg")
else:
    raise OSError("サポートされていない OS です")

settings_path="settings.txt"
if not os.path.exists(settings_path):
    with open(settings_path, "w", encoding="utf-8") as f:
        f.write("quality=360p\nformat=mp4\nsave_path=C:\\path\\to\\save\n")
settings = {}
with open(settings_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if "=" in line:
            key, value = line.split("=", 1)
            settings[key] = value
quality=settings["quality"]
format=settings["format"]
save_path=settings["save_path"]

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
combo1=ttk.Combobox(frame_3_1,state="readonly",textvariable=quality_option,values=["144p","240p","360p","480p","720p","1080p"])
frame_3_2=tk.Frame(frame_3)
label_3=ttk.Label(frame_3_2,
                text="フォーマットを選択",
                foreground="#FFFFFF",
                font=(standard_font,12),
                padding=(0,0))
format_option=StringVar()
combo2=ttk.Combobox(frame_3_2,state="readonly",textvariable=format_option,values=["mp4","mp3","wav"])
combo2.config(state="normal")
combo2.delete(0,tk.END)
combo2.insert(0,format)
combo2.config(state="readonly")
#画質選択肢更新用関数
def update_quality_options(event=None):
    fmt = combo2.get()
    if fmt in ("mp3"):
        combo1["values"] = ["64","96","128","160","192","256"]
        combo1.current(2)
        label_2["text"]=["音質(kbps)を選択"]
    elif fmt in ("mp4"):
        combo1['values'] = ["144p","240p","360p","480p","720p","1080p"]
        combo1.current(4)
        label_2["text"]=["画質を選択"]
    elif fmt in ("wav"):
        combo1["values"]=[]
        combo1.config(state="normal")
        combo1.delete(0,tk.END)
        combo1.config(state="readonly")
        label_2["text"]=["選択肢無し"]
combo2.bind("<<ComboboxSelected>>", update_quality_options)
update_quality_options()
combo1.config(state="normal")
combo1.delete(0,tk.END)
combo1.insert(0,quality)
combo1.config(state="readonly")

frame_4=tk.Frame(root)
label_4=ttk.Label(frame_4,
                  text="保存先:",
                  foreground="#FFFFFF",
                  font=(standard_font,12),
                  padding=(0,0))
entry_1=ttk.Entry(frame_4,state="readonly")
entry_1.config(state="normal")
entry_1.insert(0, save_path)
entry_1.config(state="readonly")
button_1=ttk.Button(frame_4,text="参照",command=lambda:select_folder(entry_1))
def select_folder(entry_widget):
    folder_path = filedialog.askdirectory()
    if folder_path:  # キャンセルされなければ
        entry_widget.config(state="normal")
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, folder_path)
        entry_widget.config(state="readonly")


frame_5=tk.Frame(root)
button_2=ttk.Button(frame_5,text="現在の設定を保存",command=lambda:save_settings())
def save_settings():
    question=messagebox.askyesno("確認","現在の画質、フォーマット、保存先の情報を規定値に設定しますか？")
    if question:
        settings={
            "quality":combo1.get(),
            "format":combo2.get(),
            "save_path":entry_1.get(),
        }
        with open(settings_path, "w", encoding="utf-8") as f:
            for key, value in settings.items():
                f.write(f"{key}={value}\n")
button_3=ttk.Button(frame_5,text="オプション")
button_4=ttk.Button(frame_5,text="ダウンロード開始",command=lambda:download())

def download():
    if combo2.get()=="mp4":
        url=text_1.get("1.0", "end-1c").strip()
        save_path=entry_1.get()
        if not url:
            messagebox.showerror("エラー", "URLが入力されていません")
            return
        max_quality=1080
        min_quality=int((combo1.get()).replace("p",""))
        ydl_opts={}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl: #ダウンロードせずに情報を取得
            info = ydl.extract_info(url, download=False)
            formats = info['formats']
            candidates = [
                f for f in formats
                if f.get('height')  # 動画ストリームであること
                and min_quality <= f['height'] <= max_quality
                and f.get('vcodec') != 'none'  # 映像付き
            ]
            if not candidates:
                messagebox.showerror("","希望の画質をYouTubeから習得することができませんでした。")
            selected = min(candidates, key=lambda x: x['height'])
            format_id=selected["format_id"]
        ydl_opts={
            "format": f"{format_id}+bestaudio/best",
            'merge_output_format': 'mp4',
            'ffmpeg_location': ffmpeg_path ,
            "outtmpl": os.path.join(save_path, "%(title)s.%(ext)s"),
        }
        print(format_id)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    
    elif combo2.get()=="mp3":
        url=text_1.get("1.0", "end-1c").strip()
        save_path=entry_1.get()
        if not url:
            messagebox.showerror("エラー", "URLが入力されていません")
            return
        kbps=combo1.get()
        ydl_opts={
            "format": "bestaudio/best",
            "ffmpeg_location": ffmpeg_path,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": kbps,
            }],
            "outtmpl": os.path.join(save_path, "%(title)s.%(ext)s"),
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    elif combo2.get() == "wav":
        url = text_1.get("1.0", "end-1c").strip()
        save_path=entry_1.get()
        if not url:
            messagebox.showerror("エラー", "URLが入力されていません")
            return
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(save_path, "%(title)s.%(ext)s"),
            "ffmpeg_location": ffmpeg_path,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

frame_1.pack(fill="x",padx=10,pady=2)
label_1.pack(side="left")

frame_2.pack(fill="x",padx=3,pady=2)
text_1.pack(fill="x")

frame_3.pack(fill="x",padx=10,pady=2)
frame_3_2.pack(side="left", fill="both", expand=True)
label_2.pack(side="left",anchor="w", padx=5, pady=5)
combo1.pack(side="left",anchor="w",padx=5)
frame_3_1.pack(side="left", fill="both", expand=True)
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