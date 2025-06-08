#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os

class SmartFolderCreator(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Smart Folder Creator")
        self.geometry("600x700")

        # Main container
        main = ttk.Frame(self, padding="10")
        main.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Same GUI elements as before, but removing observer-related code
        ttk.Label(main, text="Smart Folder Name:").grid(row=0, column=0, sticky=tk.W)
        self.folder_name = ttk.Entry(main, width=40)
        self.folder_name.grid(row=0, column=1, sticky=tk.W, pady=5)

        ttk.Label(main, text="Search In:").grid(row=1, column=0, sticky=tk.W)
        self.search_dir = ttk.Entry(main, width=40)
        self.search_dir.grid(row=1, column=1, sticky=tk.W, pady=5)
        self.search_dir.insert(0, os.path.expanduser("~"))
        ttk.Button(main, text="Browse", command=self.browse_directory).grid(row=1, column=2, padx=5)

        # Age Filter
        age_frame = ttk.LabelFrame(main, text="Age Filter", padding="5")
        age_frame.grid(row=2, column=0, columnspan=3, sticky=tk.W+tk.E, pady=10)

        self.age_var = tk.StringVar(value="any")
        ttk.Radiobutton(age_frame, text="Any age", variable=self.age_var, value="any").grid(row=0, column=0)
        ttk.Radiobutton(age_frame, text="Last X days:", variable=self.age_var, value="days").grid(row=1, column=0)
        self.days_entry = ttk.Entry(age_frame, width=5)
        self.days_entry.insert(0, "7")
        self.days_entry.grid(row=1, column=1)

        # Size Filter
        size_frame = ttk.LabelFrame(main, text="Size Filter", padding="5")
        size_frame.grid(row=3, column=0, columnspan=3, sticky=tk.W+tk.E, pady=10)

        self.size_var = tk.StringVar(value="any")
        ttk.Radiobutton(size_frame, text="Any size", variable=self.size_var, value="any").grid(row=0, column=0)
        ttk.Radiobutton(size_frame, text="Larger than:", variable=self.size_var, value="larger").grid(row=1, column=0)
        self.size_entry = ttk.Entry(size_frame, width=5)
        self.size_entry.insert(0, "100")
        self.size_entry.grid(row=1, column=1)
        ttk.Label(size_frame, text="MB").grid(row=1, column=2)

        # File Types
        types_frame = ttk.LabelFrame(main, text="File Types", padding="5")
        types_frame.grid(row=4, column=0, columnspan=3, sticky=tk.W+tk.E, pady=10)

        self.file_types = {
            'Documents': ['.txt', '.doc', '.docx', '.pdf', '.odt', '.rtf', '.md'],
            'Scripts': ['.py', '.sh', '.bash', '.js', '.pl', '.rb', '.php'],
            'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.psd', '.webp'],
            'Videos': ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v'],
            'Audio': ['.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac', '.wma']
        }

        self.type_vars = {}
        for i, (category, _) in enumerate(self.file_types.items()):
            self.type_vars[category] = tk.BooleanVar(value=False)
            ttk.Checkbutton(types_frame, text=category, variable=self.type_vars[category]).grid(row=i//2, column=i%2, sticky=tk.W)

        # Exclusions
        excl_frame = ttk.LabelFrame(main, text="Exclusions", padding="5")
        excl_frame.grid(row=5, column=0, columnspan=3, sticky=tk.W+tk.E, pady=10)

        self.exclude_common = tk.BooleanVar(value=True)
        ttk.Checkbutton(excl_frame, text="Exclude common system files and directories",
                      variable=self.exclude_common).grid(row=0, column=0, sticky=tk.W)

        # Create Button
        ttk.Button(main, text="Create Smart Folder", command=self.create_smart_folder).grid(row=6, column=0, columnspan=3, pady=20)

        # Status
        self.status_var = tk.StringVar()
        ttk.Label(main, textvariable=self.status_var, wraplength=580).grid(row=7, column=0, columnspan=3)

    def browse_directory(self):
        directory = filedialog.askdirectory(initialdir=os.path.expanduser("~"))
        if directory:
            self.search_dir.delete(0, tk.END)
            self.search_dir.insert(0, directory)

    def create_smart_folder(self):
        name = self.folder_name.get().strip()
        if not name:
            self.status_var.set("Please enter a folder name")
            return

        target_dir = os.path.join(os.path.expanduser("~"), ".smart_folders", name)
        if os.path.exists(target_dir):
            if not messagebox.askyesno("Folder Exists",
                f"Smart folder '{name}' already exists. Overwrite?"):
                return

        find_args = []

        if self.age_var.get() == "days":
            try:
                days = int(self.days_entry.get())
                find_args.append(f"-mtime -{days}")
            except ValueError:
                pass

        if self.size_var.get() == "larger":
            try:
                size = int(self.size_entry.get())
                find_args.append(f"-size +{size}M")
            except ValueError:
                pass

        type_patterns = []
        for category, var in self.type_vars.items():
            if var.get():
                type_patterns.extend(f"""'-iname "*.{ext[1:]}"'""" for ext in self.file_types[category])

        if type_patterns:
            find_args.append("\\( " + " -o ".join(type_patterns) + " \\)")

        if find_args:
            find_args = ['-type f'] + find_args

        if self.exclude_common.get():
            find_args.extend([
                "-not -path '*/\\.*/*'",
                "-not -path '*/node_modules/*'",
                "-not -path '*/venv/*'",
                "-not -path '*/cache/*'"
            ])

        script_path = os.path.join(os.path.dirname(__file__), "smart-folders.sh")
        cmd = f"{script_path} create {name} '{self.search_dir.get()}' '{' '.join(find_args)}'"
        print(f"\nGenerated command:\n{cmd}\n")

        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                self.status_var.set(
                    f"Smart folder created at ~/.smart_folders/{name}/ (updates handled by system service)")
            else:
                self.status_var.set(f"Error: {result.stderr}")
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")

if __name__ == "__main__":
    app = SmartFolderCreator()
    app.mainloop()
