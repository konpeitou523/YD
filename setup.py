import os
import stat
import sys
import subprocess

def ensure_ffmpeg_and_ffprobe_executable(ffmpeg_dir):
    """
    ffmpeg と ffprobe のバイナリに実行権限を付与し、
    macOS の場合は Gatekeeper のブロック属性を解除する関数
    """
    ffmpeg_path = os.path.join(ffmpeg_dir, "ffmpeg")
    ffprobe_path = os.path.join(ffmpeg_dir, "ffprobe")

    for path in [ffmpeg_path, ffprobe_path]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"{os.path.basename(path)} が見つかりません: {path}")

        # 実行権限を付与
        st = os.stat(path)
        os.chmod(path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

        # macOS の場合、quarantine 属性を削除
        if sys.platform == "darwin":
            try:
                subprocess.run(["xattr", "-d", "com.apple.quarantine", path],
                               check=True, capture_output=True)
            except subprocess.CalledProcessError:
                # 属性がなければ無視
                pass

        # 実行確認
        try:
            result = subprocess.run([path, "-version"],
                                    capture_output=True, text=True, check=True)
            print(f"{os.path.basename(path)} version:\n", result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"{os.path.basename(path)} を実行できません:", e.stderr)

# 使用例
ffmpeg_dir = os.path.join(os.path.dirname(__file__), "ffmpeg")
ensure_ffmpeg_and_ffprobe_executable(ffmpeg_dir)
