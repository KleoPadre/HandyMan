import os
import shutil
import subprocess
from PIL import Image  # Add this import at the beginning of the file


def get_video_duration(file_path):
    ffprobe_path = os.environ.get("FFPROBE_PATH", "ffprobe")
    try:
        result = subprocess.run(
            [
                ffprobe_path,
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                file_path,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return float(result.stdout.strip())
    except (subprocess.SubprocessError, FileNotFoundError, ValueError):
        return None


def move_short_videos(
    source_folder, destination_folder, log_callback, progress_callback, check_if_running
):
    video_formats = (".mp4", ".mov", ".wmv", ".avi", ".flv", ".f4v", ".mkv", ".m4v")
    total_files = 0
    processed_files = 0
    moved_files = 0

    # Count total video files
    log_callback("Counting files...")
    for root, _, files in os.walk(source_folder):
        for file in files:
            if file.lower().endswith(video_formats):
                total_files += 1

    log_callback(f"Found {total_files} video files")

    if total_files == 0:
        log_callback("No video files found.")
        progress_callback(0, 0, 0, "")  # current, total, percentage, filename
        return

    # Move short videos
    for root, _, files in os.walk(source_folder):
        for file in files:
            if not check_if_running():
                return  # Stop execution if operation is cancelled
            if file.lower().endswith(video_formats):
                # Get relative path from source folder
                rel_path = os.path.relpath(root, source_folder)
                # Create the same path in destination folder
                dest_dir = os.path.join(destination_folder, rel_path)

                file_path = os.path.join(root, file)
                processed_files += 1

                try:
                    # Update progress with current file
                    percentage = int((processed_files / total_files) * 100)
                    progress_callback(processed_files, total_files, percentage, file)

                    duration = get_video_duration(file_path)
                    if duration is not None and duration <= 3:
                        # Create destination folder if it doesn't exist
                        os.makedirs(dest_dir, exist_ok=True)
                        # Move file while preserving folder structure
                        dest_file = os.path.join(dest_dir, file)
                        shutil.move(file_path, dest_file)
                        moved_files += 1
                        log_callback(f"Moved: {os.path.join(rel_path, file)}")
                    else:
                        duration_str = (
                            f"{duration:.2f}s" if duration is not None else "unknown"
                        )
                        log_callback(
                            f"Skipped: {os.path.join(rel_path, file)} (duration: {duration_str})"
                        )
                except Exception as e:
                    log_callback(f"Error processing {file}: {str(e)}")

    # Final progress update
    progress_callback(total_files, total_files, 100, "Complete")
    log_callback(f"Moved {moved_files} out of {total_files} video files.")


def move_screenshots(
    source_folder, destination_folder, log_callback, progress_callback, check_if_running
):
    image_formats = (".png", ".jpg", ".jpeg", ".tiff", ".bmp")
    total_files = 0
    processed_files = 0
    moved_files = 0

    # Count total files
    log_callback("Counting files...")
    for root, _, files in os.walk(source_folder):
        for file in files:
            if file.lower().endswith(image_formats):
                total_files += 1

    log_callback(f"Found {total_files} images")

    if total_files == 0:
        log_callback("No images found.")
        progress_callback(0, 0, 0, "")
        return

    # Move screenshots
    for root, _, files in os.walk(source_folder):
        for file in files:
            if not check_if_running():
                return  # Stop execution if operation is cancelled
            if file.lower().endswith(image_formats):
                rel_path = os.path.relpath(root, source_folder)
                dest_dir = os.path.join(destination_folder, rel_path)
                file_path = os.path.join(root, file)
                processed_files += 1

                try:
                    # Update progress
                    percentage = int((processed_files / total_files) * 100)
                    progress_callback(processed_files, total_files, percentage, file)

                    # Check EXIF data
                    with Image.open(file_path) as img:
                        is_screenshot = False

                        # Check EXIF
                        if hasattr(img, "_getexif") and img._getexif() is not None:
                            exif = img._getexif()
                            if exif:
                                for tag, value in exif.items():
                                    if value is None:
                                        continue
                                    value = str(value).lower()
                                    if "screenshot" in value:
                                        is_screenshot = True
                                        break

                        # If it's a screenshot, move the file
                        if is_screenshot:
                            os.makedirs(dest_dir, exist_ok=True)
                            dest_file = os.path.join(dest_dir, file)
                            shutil.move(file_path, dest_file)
                            moved_files += 1
                            log_callback(f"Moved: {os.path.join(rel_path, file)}")

                except Exception as e:
                    log_callback(f"Error processing {file}: {str(e)}")

    # Final progress update
    progress_callback(total_files, total_files, 100, "Complete")
    log_callback(f"Moved {moved_files} out of {total_files} images.")
