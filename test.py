import subprocess
import os


ffmpeg_path = os.path.join(os.path.dirname(__file__), "ffmpeg","ffmpeg")
subprocess.run([ffmpeg_path, "-version"])