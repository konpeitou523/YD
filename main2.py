import os
import sys
import threading
import tkinter as tk
from tkinter import Tk, StringVar, filedialog, ttk, messagebox
import yt_dlp
import re

# --- OS に応じた ffmpeg パス ---
if sys.platform == "win32":
    ffmpeg_path = os.path.join(os.path.dirname(__file__), "ffmpeg", "ffmpeg.exe")
elif sys.platform == "darwin":
    ffmpeg_path = os.path.join(os.path.dirname(__file__), "ffmpeg","ffmpeg")
else:
    raise OSError("サポートされていない OS です")

# --- 設定ファイル ---
settings_path = "settings.txt"
if not os.path.exists(settings_path):
    with open(settings_path, "w", encoding="utf-8") as f:
        f.write("quality=360p\nformat=mp4\nsave_path=" + os.path.expanduser("~") + "\n")

settings = {}
with open(settings_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if "=" in line:
            key, value = line.split("=", 1)
            settings[key] = value

quality = settings.get("quality", "360p")
format_ = settings.get("format", "mp4")
save_path = settings.get("save_path", os.path.expanduser("~"))

# --- GUI ---
root = Tk()
root.title("YouTube Downloader")
root.geometry("800x300")
standard_font = "Times New Roman"

# --- フォーム・ウィジェット ---
frame_1 = tk.Frame(root)
label_1 = ttk.Label(frame_1, text="YouTubeのリンクを入力", foreground="#FFFFFF", font=(standard_font, 12))
frame_2 = tk.Frame(root)
text_1 = tk.Text(frame_2, wrap="char", height=3)

frame_3 = tk.Frame(root)
frame_3_1 = tk.Frame(frame_3)
label_2 = ttk.Label(frame_3_1, foreground="#FFFFFF", font=(standard_font, 12))
quality_option = StringVar()
combo1 = ttk.Combobox(frame_3_1, state="readonly", textvariable=quality_option)
frame_3_2 = tk.Frame(frame_3)
label_3 = ttk.Label(frame_3_2, text="フォーマットを選択", foreground="#FFFFFF", font=(standard_font, 12))
format_option = StringVar()
combo2 = ttk.Combobox(frame_3_2, state="readonly", textvariable=format_option, values=["mp4", "mp3", "wav"])

frame_4 = tk.Frame(root)
label_4 = ttk.Label(frame_4, text="保存先:", foreground="#FFFFFF", font=(standard_font, 12))
entry_1 = ttk.Entry(frame_4, state="readonly")
entry_1.config(state="normal")
entry_1.insert(0, save_path)
entry_1.config(state="readonly")
button_1 = ttk.Button(frame_4, text="参照", command=lambda: select_folder(entry_1))

frame_5 = tk.Frame(root)
button_2 = ttk.Button(frame_5, text="現在の設定を保存", command=lambda: save_settings())
button_3 = ttk.Button(frame_5, text="オプション")
button_4 = ttk.Button(frame_5, text="ダウンロード開始", command=lambda: download_threaded())

# --- フォルダ選択 ---
def select_folder(entry_widget):
    folder_path = filedialog.askdirectory()
    if folder_path:
        entry_widget.config(state="normal")
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, folder_path)
        entry_widget.config(state="readonly")

# --- 設定保存 ---
def save_settings():
    question = messagebox.askyesno("確認", "現在の画質、フォーマット、保存先の情報を規定値に設定しますか？")
    if question:
        settings = {
            "quality": combo1.get(),
            "format": combo2.get(),
            "save_path": entry_1.get(),
        }
        with open(settings_path, "w", encoding="utf-8") as f:
            for key, value in settings.items():
                f.write(f"{key}={value}\n")

# --- 画質/音質選択肢更新 ---
def update_quality_options(event=None):
    fmt = combo2.get()
    if fmt == "mp3":
        combo1["values"] = ["64", "96", "128", "160", "192", "256"]
        combo1.current(2)
        label_2["text"] = "音質(kbps)を選択"
    elif fmt == "mp4":
        combo1['values'] = ["144p", "240p", "360p", "480p", "720p", "1080p"]
        combo1.current(4)
        label_2["text"] = "画質を選択"
    elif fmt == "wav":
        combo1["values"] = []
        combo1.set("")
        label_2["text"] = "選択肢無し"

combo2.bind("<<ComboboxSelected>>", update_quality_options)
combo2.set(format_)
update_quality_options()
combo1.set(quality)

# --- プログレス表示 ---
def show_progress_window():
    progress_win = tk.Toplevel(root)
    progress_win.title("ダウンロード進捗")
    progress_win.geometry("400x100")
    progress_label = ttk.Label(progress_win, text="0%", font=(standard_font, 12))
    progress_label.pack(pady=10)
    progress_bar = ttk.Progressbar(progress_win, orient="horizontal", length=300, mode="determinate")
    progress_bar.pack(pady=10)
    return progress_win, progress_label, progress_bar

def create_progress_hook(progress_win, progress_label, progress_bar):
    def progress_hook(d):
        if d['status'] == 'downloading':
            percent_str = d.get('_percent_str', '0.0').strip()
            eta = d.get('eta')
            try:
                eta_int = int(float(eta)) if eta is not None else 0
            except (ValueError, TypeError):
                eta_int = 0
            progress_label.config(text=f"{percent_str} 残り {eta_int}秒")
            progress_bar['value'] = float(percent_str.replace('%',''))
        elif d['status'] == 'finished':
            progress_label.config(text="変換完了")
            progress_bar['value'] = 100
            # コンバート完了時にウィンドウを閉じてメッセージ表示
            progress_win.destroy()
            messagebox.showinfo("完了", "動画のコンバートが終了しました")
    return progress_hook



def download_threaded():
    progress_win, progress_label, progress_bar = show_progress_window()
    hook = create_progress_hook(progress_win, progress_label, progress_bar)
    threading.Thread(target=lambda: download(progress_hook=hook), daemon=True).start()

# --- ダウンロード処理 ---
def download(progress_hook=None):
    url = text_1.get("1.0", "end-1c").strip()
    save_path = entry_1.get()
    if not url:
        messagebox.showerror("エラー", "URLが入力されていません")
        return

    ydl_opts_common = {
        "ffmpeg_location": ffmpeg_path,
        "progress_hooks": [progress_hook] if progress_hook else None,
        "outtmpl": os.path.join(save_path, "%(title)s.%(ext)s"),
        "nocolor": True,
    }

    if combo2.get() == "mp4":
        max_quality=1080
        min_quality=int(combo1.get().replace("p",""))
        with yt_dlp.YoutubeDL({}) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info['formats']
            candidates = [f for f in formats if f.get('height') and min_quality <= f['height'] <= max_quality and f.get('vcodec') != 'none']
            if not candidates:
                messagebox.showerror("", "希望の画質をYouTubeから取得できませんでした。")
                return
            selected = min(candidates, key=lambda x: x['height'])
            format_id = selected["format_id"]

        ydl_opts = ydl_opts_common.copy()
        ydl_opts.update({
            "format": f"{format_id}+bestaudio/best",
            "merge_output_format": "mp4",
        })

    elif combo2.get() == "mp3":
        kbps = combo1.get()
        ydl_opts = ydl_opts_common.copy()
        ydl_opts.update({
            "format": "bestaudio/best",
            "postprocessors": [{"key":"FFmpegExtractAudio","preferredcodec":"mp3","preferredquality":kbps}],
        })

    elif combo2.get() == "wav":
        ydl_opts = ydl_opts_common.copy()
        ydl_opts.update({
            "format": "bestaudio/best",
            "postprocessors": [{"key":"FFmpegExtractAudio","preferredcodec":"wav"}],
        })

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# --- 配置 ---
frame_1.pack(fill="x", padx=10, pady=2); label_1.pack(side="left")
frame_2.pack(fill="x", padx=3, pady=2); text_1.pack(fill="x")
frame_3.pack(fill="x", padx=10, pady=2)
frame_3_2.pack(side="left", fill="both", expand=True)
label_2.pack(side="left", anchor="w", padx=5, pady=5)
combo1.pack(side="left", anchor="w", padx=5)
frame_3_1.pack(side="left", fill="both", expand=True)
label_3.pack(side="left", anchor="w", padx=5, pady=5)
combo2.pack(side="left", anchor="w", padx=5)
frame_4.pack(fill="x", padx=10, pady=2)
frame_4.columnconfigure(1, weight=1)
label_4.grid(row=0,column=0); entry_1.grid(row=0,column=1,sticky="ew",padx=5); button_1.grid(row=0,column=2)
frame_5.pack(fill="x", padx=10, pady=2, side="bottom")
frame_5.columnconfigure(0, weight=1)
button_2.grid(row=0,column=1,padx=5); button_3.grid(row=0,column=2,padx=5); button_4.grid(row=0,column=3,padx=5)

root.mainloop()
