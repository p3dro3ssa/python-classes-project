import tkinter as tk
from tkinter import filedialog
import zipfile
import os


def select_file():
    """Opens a dialog to select the .pak file."""
    root = tk.Tk()
    root.withdraw()
    path = filedialog.askopenfilename(
        title="Select Dying Light 2 .pak file",
        filetypes=[("PAK Files", "*.pak"), ("All Files", "*.*")]
    )
    return path


def check_header(path):
    """Checks if the file starts with the ZIP magic bytes."""
    with open(path, 'rb') as f:
        header = f.read(4)
    return header == b'PK\x03\x04'


def scan_pak(path):
    """Extracts and displays insights from the .pak file."""
    print(f"\n{'=' * 50}")
    print(f"ANALYZING: {os.path.basename(path)}")
    print(f"{'=' * 50}")

    if not check_header(path):
        print("Result: This is NOT a standard ZIP-based .pak file.")
        return

    try:
        with zipfile.ZipFile(path, 'r') as pak:
            file_list = pak.infolist()
            total_files = len(file_list)

            print(f"Format: Valid ZIP-based Archive")
            print(f"Total Files Found: {total_files}")
            print(f"{'-' * 50}")
            print(f"{'File Path':<50} | {'Size (KB)':<10}")
            print(f"{'-' * 50}")

            # Display the first 15 files as a sample
            for info in file_list[:15]:
                size_kb = round(info.file_size / 1024, 2)
                print(f"{info.filename[:50]:<50} | {size_kb:<10}")

            if total_files > 15:
                print(f"\n... and {total_files - 15} more files.")

    except zipfile.BadZipFile:
        print("Error: The file is corrupted or not a valid ZIP.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    selected_path = select_file()
    if selected_path:
        scan_pak(selected_path)
    else:
        print("No file selected.")





























