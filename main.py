import tkinter as tk
from tkinter import filedialog, messagebox
import zipfile
import os


class InternalFileSelector:
    """A pop-up window to browse and search files inside a .pak archive."""

    def __init__(self, parent, file_list):
        self.root = tk.Toplevel(parent)
        self.root.title("Internal .pak Browser")
        self.root.geometry("600x500")

        self.original_list = sorted(file_list)
        self.selected_file = None

        # Search UI
        tk.Label(self.root, text="Search internal files:", font=('Arial', 10, 'bold')).pack(pady=5)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.update_list)
        tk.Entry(self.root, textvariable=self.search_var).pack(fill="x", padx=20, pady=5)

        # Listbox
        self.frame = tk.Frame(self.root)
        self.frame.pack(expand=True, fill="both", padx=20, pady=10)
        self.scrollbar = tk.Scrollbar(self.frame)
        self.scrollbar.pack(side="right", fill="y")
        self.listbox = tk.Listbox(self.frame, yscrollcommand=self.scrollbar.set, font=('Consolas', 9))
        self.listbox.pack(expand=True, fill="both", side="left")
        self.scrollbar.config(command=self.listbox.yview)

        tk.Button(self.root, text="Add to Staging Queue", bg="#4CAF50", fg="white",
                  command=self.confirm_selection, height=2).pack(pady=10, fill="x", padx=20)

        self.update_list()
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


class ModDashboard:
    """The main application dashboard."""

    def __init__(self, root):
        self.root = root
        self.root.title("Dying Light 2 Mod Manager")
        self.root.geometry("800x500")

        self.staging_queue = []  # List of dicts: {'source': path, 'internal': path}

        # --- UI Setup ---
        self.setup_ui()

    def setup_ui(self):
        # Left Side: Queue Display
        self.list_frame = tk.Frame(self.root)
        self.list_frame.pack(side="left", expand=True, fill="both", padx=10, pady=10)

        tk.Label(self.list_frame, text="Staging Queue (Files to be Packed):", font=("Arial", 10, "bold")).pack()
        self.queue_listbox = tk.Listbox(self.list_frame, font=("Consolas", 9))
        self.queue_listbox.pack(expand=True, fill="both", pady=5)

        # Right Side: Controls
        self.ctrl_frame = tk.Frame(self.root)
        self.ctrl_frame.pack(side="right", fill="y", padx=10, pady=10)

        tk.Button(self.ctrl_frame, text="Add File from .pak", width=25, command=self.action_add_pak).pack(pady=5)
        tk.Button(self.ctrl_frame, text="Remove Selected", width=25, command=self.action_remove).pack(pady=5)

        tk.Frame(self.ctrl_frame, height=2, bd=1, relief="sunken").pack(fill="x", pady=20)

        tk.Button(self.ctrl_frame, text="BUILD MOD .PAK", width=25, bg="#2196F3", fg="white",
                  font=("Arial", 10, "bold"), command=self.action_build).pack(side="bottom", pady=10)

    def action_add_pak(self):
        pak_path = filedialog.askopenfilename(title="Select Source .pak", filetypes=[("PAK Files", "*.pak")])
        if not pak_path: return

        try:
            with zipfile.ZipFile(pak_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()

            selector = InternalFileSelector(self.root, file_list)
            if selector.selected_file:
                self.add_to_queue(pak_path, selector.selected_file)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read .pak: {e}")

    def add_to_queue(self, source, internal):
        # Duplicate Check
        for i, item in enumerate(self.staging_queue):
            if item['internal'] == internal:
                if messagebox.askyesno("Duplicate", f"'{internal}' is already staged.\nReplace it?"):
                    self.staging_queue[i] = {'source': source, 'internal': internal}
                    self.refresh_listbox()
                return

        self.staging_queue.append({'source': source, 'internal': internal})
        self.refresh_listbox()

    def action_remove(self):
        selection = self.queue_listbox.curselection()
        if selection:
            del self.staging_queue[selection[0]]
            self.refresh_listbox()

    def refresh_listbox(self):
        self.queue_listbox.delete(0, tk.END)
        for item in self.staging_queue:
            display = f"{item['internal']}  <-- ({os.path.basename(item['source'])})"
            self.queue_listbox.insert(tk.END, display)

    def action_build(self):
        if not self.staging_queue:
            messagebox.showwarning("Empty", "Add files to the queue first!")
            return

        out_path = filedialog.asksaveasfilename(title="Save Mod", initialfile="data_my_mod.pak",
                                                filetypes=[("PAK Files", "*.pak")])
        if not out_path: return

        try:
            with zipfile.ZipFile(out_path, 'w', compression=zipfile.ZIP_DEFLATED) as master:
                for item in self.staging_queue:
                    with zipfile.ZipFile(item['source'], 'r') as src:
                        master.writestr(item['internal'], src.read(item['internal']))
            messagebox.showinfo("Success", "Mod .pak created successfully!")
        except Exception as e:
            messagebox.showerror("Build Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = ModDashboard(root)
    root.mainloop()