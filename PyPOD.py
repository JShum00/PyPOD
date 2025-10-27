# podit.py
import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from POD_Handling import PodFile

class PoditGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PyPOD | POD Extractor")
        self.geometry("650x450")

        # Toolbar
        toolbar = tk.Frame(self)
        tk.Button(toolbar, text="Open POD", command=self.open_pod).pack(side="left", padx=4, pady=4)
        tk.Button(toolbar, text="Extract Selected", command=self.extract_selected).pack(side="left", padx=4, pady=4)
        tk.Button(toolbar, text="Extract All", command=self.extract_all).pack(side="left", padx=4, pady=4)
        toolbar.pack(fill="x")

        # Frame to hold tree + scrollbars
        tree_frame = tk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=4, pady=4)

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")

        # Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("size",),
            show="tree headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )

        # Configure headings
        self.tree.heading("size", text="Size (bytes)")
        self.tree.column("size", width=120, anchor="e")

        # Pack everything nicely
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)

        # Link scrollbars to treeview
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)


        # Status bar
        self.status = tk.StringVar(value="Ready")
        tk.Label(self, textvariable=self.status, anchor="w").pack(fill="x", side="bottom")

        self.pod = None

    def open_pod(self):
        """Open a .POD or .EPD archive and list its contents."""
        path = filedialog.askopenfilename(
            title="Open POD file",
            filetypes=[("POD files", "*.pod *.POD *.epd *.EPD"), ("All files", "*.*")]
        )

        if not path:
            return
        try:
            self.pod = PodFile(path)
            self.tree.delete(*self.tree.get_children())
            for i, entry in enumerate(self.pod.entries):
                self.tree.insert("", "end", iid=f"{i}", text=entry.name, values=(entry.size,))
            self.status.set(f"Loaded {len(self.pod.entries)} files from {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open POD file:\n{e}")

    def extract_selected(self):
        """Extract only selected entries to a folder."""
        if not self.pod:
            messagebox.showinfo("No file", "Please open a POD archive first.")
            return
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("No selection", "Select one or more files to extract.")
            return

        outdir = filedialog.askdirectory(title="Choose destination folder")
        if not outdir:
            return

        for item_id in selection:
            file_name = self.tree.item(item_id, "text")
            entry = next((e for e in self.pod.entries if e.name == file_name), None)

            if not entry:
                continue
            try:
                with open(self.pod.path, "rb") as src:
                    src.seek(entry.offset)
                    data = src.read(entry.size)
                # Clean up slashes for cross-platform extraction
                normalized_path = entry.name.replace("\\", "/")  # unify slashes
                dest_path = os.path.join(outdir, normalized_path)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)

                with open(dest_path, "wb") as f:
                    f.write(data)
            except Exception as e:
                messagebox.showerror("Extraction error", f"Could not extract {entry.name}:\n{e}")

        self.status.set(f"Extracted {len(selection)} file(s)")

    def extract_all(self):
        """Extract all entries in the current POD."""
        if not self.pod:
            messagebox.showinfo("No file", "Please open a POD archive first.")
            return

        outdir = filedialog.askdirectory(title="Choose destination folder")
        if not outdir:
            return

        self.pod.extract(outdir)
        self.status.set(f"Extracted all {len(self.pod.entries)} files to {outdir}")

if __name__ == "__main__":
    PoditGUI().mainloop()

