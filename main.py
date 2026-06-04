import tkinter as tk
from tkinter import filedialog, messagebox
import zipfile
import os


class InternalFileSelector:
    def __init__(self, file_list):
        self.root = tk.Toplevel()
        self.root.title("Internal .pak Browser")
        self.root.geometry("700x500")

        self.original_list = sorted(file_list)
        self.selected_file = None

        # UI Elements
        tk.Label(self.root, text="Search for a file inside the .pak:", font=('Arial', 10, 'bold')).pack(pady=5)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.update_list)
        self.search_entry = tk.Entry(self.root, textvariable=self.search_var)
        self.search_entry.pack(fill="x", padx=20, pady=5)

        self.frame = tk.Frame(self.root)
        self.frame.pack(expand=True, fill="both", padx=20, pady=10)

        self.scrollbar = tk.Scrollbar(self.frame)
        self.scrollbar.pack(side="right", fill="y")

        self.listbox = tk.Listbox(self.frame, yscrollcommand=self.scrollbar.set, font=('Consolas', 9))
        self.listbox.pack(expand=True, fill="both", side="left")
        self.scrollbar.config(command=self.listbox.yview)

        self.btn = tk.Button(self.root, text="Select File to Swap", bg="#4CAF50", fg="white",
                             command=self.confirm_selection, height=2)
        self.btn.pack(pady=10, fill="x", padx=20)

        self.update_list()

        # This makes the main script wait until this window is closed
        self.root.grab_set()
        self.root.wait_window()
    def update_list(self, *args):
        search_term = self.search_var.get().lower()
        self.listbox.delete(0, tk.END)
        for name in self.original_list:
            if search_term in name.lower():
                self.listbox.insert(tk.END, name)

    def confirm_selection(self):
        selection = self.listbox.curselection()
        if selection:
            self.selected_file = self.listbox.get(selection[0])
            self.root.destroy()
        else:
            messagebox.showwarning("Selection Required", "Please select a file from the list first!")


def rebuild_pak(original_path, target_internal_path, replacement_disk_path):
    """
    Creates a new .pak file, copying all files from the original
    except the target, which is replaced by the new file.
    """
    # Create a name for the new file
    folder = os.path.dirname(original_path)
    new_filename = "modded_" + os.path.basename(original_path)
    output_path = os.path.join(folder, new_filename)

    print(f"Creating: {new_filename}...")

    try:
        with zipfile.ZipFile(original_path, 'r') as old_pak:
            with zipfile.ZipFile(output_path, 'w', compression=zipfile.ZIP_DEFLATED) as new_pak:

                for item in old_pak.infolist():
                    # Case 1: This is the file we want to replace
                    if item.filename == target_internal_path:
                        print(f"-> Injecting new version of: {item.filename}")
                        with open(replacement_disk_path, 'rb') as f:
                            new_pak.writestr(item.filename, f.read())

                    # Case 2: This is a normal file, just copy it
                    else:
                        # We read the data from the old and write to the new
                        new_pak.writestr(item, old_pak.read(item.filename))

        print(f"\nSUCCESS! Your modded file is located at:\n{output_path}")
        messagebox.showinfo("Success", f"Modded file created:\n{new_filename}")

    except Exception as e:
        print(f"An error occurred during reconstruction: {e}")
        messagebox.showerror("Error", f"Failed to rebuild .pak: {e}")

def get_pak_content(path):
    """Returns a list of filenames inside the .pak."""
    try:
        with zipfile.ZipFile(path, 'r') as pak:
            return pak.namelist()
    except Exception as e:
        messagebox.showerror("Error", f"Could not read .pak: {e}")
        return []


def main():
    # 1. Hide the main empty Tkinter window
    root = tk.Tk()
    root.withdraw()

    # 2. Select the .pak file
    pak_path = filedialog.askopenfilename(title="Select .pak File", filetypes=[("PAK Files", "*.pak")])
    if not pak_path:
        return

    # 3. Get contents and open our custom selector
    print("Reading .pak index...")
    internal_files = get_pak_content(pak_path)

    if internal_files:
        selector = InternalFileSelector(internal_files)

        if selector.selected_file:
            print(f"\nSUCCESS: You selected to swap: {selector.selected_file}")

            # 4. Now ask for the REPLACEMENT file on the computer
            replacement_path = filedialog.askopenfilename(
                title=f"Select replacement for {os.path.basename(selector.selected_file)}")

            if replacement_path:
                print(f"REPLACEMENT FILE: {replacement_path}")

                # CALL THE REBUILD LOGIC HERE
                rebuild_pak(pak_path, selector.selected_file, replacement_path)
            else:
                print("Replacement selection cancelled.")
    else:
        print("The .pak file appears to be empty or invalid.")
        # ... inside your main() function, after selecting replacement_path ...

if __name__ == "__main__":
    main()





























