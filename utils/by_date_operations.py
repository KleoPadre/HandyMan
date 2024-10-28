import os
import shutil
from datetime import datetime
from PIL import Image
import re


def extract_date_from_filename(filename):
    # Patterns for finding dates in filenames
    patterns = [
        r"IMG_(\d{8})",  # IMG_20240417
        r"(\d{4})[.-](\d{2})[.-](\d{2})",  # 2024-04-17 or 2024.04.17
        r"(\d{4})(\d{2})(\d{2})",  # 20240417
    ]

    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            try:
                if len(match.groups()) == 1:
                    # For IMG_20240417 format
                    date_str = match.group(1)
                    return datetime.strptime(date_str, "%Y%m%d")
                elif len(match.groups()) == 3:
                    # For format with separators
                    year, month, day = match.groups()
                    return datetime(int(year), int(month), int(day))
            except ValueError:
                continue
    return None


def extract_date_from_exif(file_path):
    try:
        with Image.open(file_path) as img:
            if hasattr(img, "_getexif") and img._getexif() is not None:
                exif = img._getexif()
                # List of EXIF tags that may contain creation date
                date_tags = [
                    36867,
                    36868,
                    306,
                    50971,
                ]  # DateTimeOriginal, DateTime, etc.

                for tag in date_tags:
                    if tag in exif:
                        try:
                            date_str = exif[tag]
                            # Processing various date formats in EXIF
                            for fmt in ["%Y:%m:%d %H:%M:%S", "%Y-%m-%d %H:%M:%S"]:
                                try:
                                    return datetime.strptime(
                                        date_str.split(".")[0], fmt
                                    )
                                except ValueError:
                                    continue
                        except Exception:
                            continue
    except Exception:
        pass
    return None


def should_move_folder(folder_name):
    # Check if folder contains date in YYYY.MM.DD or YYYY-MM-DD format
    date_pattern = r"\d{4}[.-]\d{2}[.-]\d{2}"
    return not re.match(date_pattern, folder_name)


def organize_by_date(
    source_folder, destination_folder, log_callback, progress_callback
):
    total_files = 0
    processed_files = 0
    moved_files = 0

    # Count files
    log_callback("Counting files...")
    for root, dirs, files in os.walk(source_folder):
        total_files += len(files)

    if total_files == 0:
        log_callback("No files found.")
        progress_callback(0, 0, 0, "")
        return

    log_callback(f"Found {total_files} files")

    for root, dirs, files in os.walk(source_folder):
        rel_path = os.path.relpath(root, source_folder)
        current_folder = os.path.basename(root)

        # Check if we need to move the entire folder
        if should_move_folder(current_folder):
            folder_date = None
            # Find creation date of first file in folder
            for file in files:
                file_path = os.path.join(root, file)
                file_date = extract_date_from_exif(file_path)
                if file_date:
                    folder_date = file_date
                    break

            if folder_date:
                # Remove date from folder name if present
                folder_name = re.sub(
                    r"^\d{2}(\.\d{2})?(\s+|$)", "", current_folder
                ).strip()

                # If folder name is empty after date removal, use original name
                if not folder_name:
                    folder_name = current_folder

                # Create destination path including cleaned folder name
                dest_path = os.path.join(
                    destination_folder,
                    str(folder_date.year),
                    f"{folder_date.month:02d}",
                    f"{folder_date.day:02d} {folder_name}".strip(),
                )
                try:
                    if not os.path.exists(dest_path):
                        shutil.copytree(root, dest_path)
                        shutil.rmtree(root)
                        log_callback(
                            f"Moved entire folder: {rel_path} -> {os.path.relpath(dest_path, destination_folder)}"
                        )
                    continue
                except Exception as e:
                    log_callback(f"Error moving folder {rel_path}: {str(e)}")
                    continue

        for file in files:
            processed_files += 1
            percentage = int((processed_files / total_files) * 100)
            progress_callback(processed_files, total_files, percentage, file)

            file_path = os.path.join(root, file)

            # Get file date
            file_date = extract_date_from_exif(file_path)

            if not file_date:
                file_date = extract_date_from_filename(file)

            if not file_date:
                log_callback(f"Could not determine date for file: {file}")
                continue

            # Create destination path
            date_path = os.path.join(
                destination_folder,
                str(file_date.year),
                f"{file_date.month:02d}",
                f"{file_date.day:02d}",
            )

            try:
                os.makedirs(date_path, exist_ok=True)
                dest_file = os.path.join(date_path, file)

                # If file already exists, add a number
                counter = 1
                base_name, ext = os.path.splitext(file)
                while os.path.exists(dest_file):
                    dest_file = os.path.join(date_path, f"{base_name}_{counter}{ext}")
                    counter += 1

                shutil.move(file_path, dest_file)
                moved_files += 1
                log_callback(
                    f"Moved: {file} -> {os.path.relpath(dest_file, destination_folder)}"
                )

            except Exception as e:
                log_callback(f"Error moving {file}: {str(e)}")

    progress_callback(total_files, total_files, 100, "Complete")
    log_callback(f"Moved {moved_files} out of {total_files} files")
