import sys
import shutil
import os
from PyQt6.QtWidgets import QApplication, QMessageBox
from ui.main_window import MainWindow

def check_ffmpeg():
    ffmpeg_paths = [
        "ffprobe",  # Check if ffprobe is available globally
        "/opt/homebrew/bin/ffprobe",  # Path for Homebrew on M1 Mac
        "/usr/local/bin/ffprobe",  # Standard path for Homebrew on Intel Mac
        "/opt/homebrew/opt/ffmpeg/bin/ffprobe",  # Alternative path for Homebrew
    ]
    
    for path in ffmpeg_paths:
        if shutil.which(path):
            os.environ["FFPROBE_PATH"] = path
            return True
    
    QMessageBox.critical(None, "Error", "FFmpeg not found. Please install FFmpeg and make sure it's in your system PATH.")
    return False

def main():
    app = QApplication([])
    if check_ffmpeg():
        window = MainWindow()
        window.show()
        app.exec()
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
