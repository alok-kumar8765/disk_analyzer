import os
import sys
import threading
import platform
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Matplotlib for modern charting
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Color Palette (Modern Dark Theme)
BG_COLOR = "#0f172a"        # Deep slate background
CARD_BG = "#1e293b"         # Lighter slate for cards/panels
TEXT_PRIMARY = "#f8fafc"    # Bright white text
TEXT_SECONDARY = "#94a3b8"  # Muted grey text
ACCENT_COLOR = "#3b82f6"    # Vibrant blue accent
ACCENT_HOVER = "#2563eb"    # Darker blue for hover
BORDER_COLOR = "#334155"    # Border color

# File type categorization dictionaries
EXT_CATEGORIES = {
    "Videos": ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v'],
    "Images": ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.tiff'],
    "Documents": ['.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.txt', '.csv', '.rtf'],
    "Audio": ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma'],
    "Archives": ['.zip', '.rar', '.7z', '.tar', '.gz', '.iso', '.bz2'],
    "Code / Dev": ['.py', '.js', '.html', '.css', '.cpp', '.h', '.json', '.xml', '.sql', '.java'],
}

def format_size(size_bytes):
    """Converts bytes to human-readable string (KB, MB, GB)."""
    if size_bytes == 0:
        return "0.00 B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = 0
    while size_bytes >= 1024 and i < len(size_name) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.2f} {size_name[i]}"

class StorageAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HELL'S KITCHEN - Advanced Disk Space Analyzer")
        self.root.geometry("1350x850")
        self.root.minsize(1100, 750)
        self.root.configure(bg=BG_COLOR)

        self.scanned_files = []
        self.category_stats = {}
        self.total_scanned_size = 0

        self.setup_styles()
        self.create_layout()

    def setup_styles(self):
        """Configures custom TTK styles for a modern look."""
        style = ttk.Style()
        style.theme_use("clam")

        # Configure generic styles
        style.configure(".", background=BG_COLOR, foreground=TEXT_PRIMARY, font=("Segoe UI", 10))
        
        # Frame styles
        style.configure("Card.TFrame", background=CARD_BG, relief="flat")
        
        # Label styles
        style.configure("TLabel", background=BG_COLOR, foreground=TEXT_PRIMARY)
        style.configure("Card.TLabel", background=CARD_BG, foreground=TEXT_PRIMARY)
        style.configure("Secondary.TLabel", background=CARD_BG, foreground=TEXT_SECONDARY, font=("Segoe UI", 9))
        style.configure("Header.TLabel", background=BG_COLOR, foreground=TEXT_PRIMARY, font=("Segoe UI", 14, "bold"))

        # Button style
        style.configure("Accent.TButton", background=ACCENT_COLOR, foreground="white", font=("Segoe UI", 10, "bold"), borderwidth=0)
        style.map("Accent.TButton", background=[("active", ACCENT_HOVER)])

        # Treeview styling
        style.configure("Treeview", 
                        background=CARD_BG, 
                        foreground=TEXT_PRIMARY, 
                        fieldbackground=CARD_BG, 
                        borderwidth=0, 
                        rowheight=28,
                        font=("Segoe UI", 9))
        style.configure("Treeview.Heading", 
                        background="#334155", 
                        foreground=TEXT_PRIMARY, 
                        font=("Segoe UI", 10, "bold"),
                        relief="flat")
        style.map("Treeview", background=[("selected", ACCENT_COLOR)])

    def create_layout(self):
        """Builds the 3-section layout UI."""
        
        # Main Container Grid
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)

        # ==========================================
        # SECTION 1: Controls & Directory Selection
        # ==========================================
        sec1_frame = ttk.Frame(self.root, style="Card.TFrame")
        sec1_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        sec1_frame.columnconfigure(1, weight=1)

        # Title / Brand
        lbl_title = ttk.Label(sec1_frame, text="HELL'S KITCHEN - Storage Analyzer", style="Header.TLabel", background=CARD_BG)
        lbl_title.grid(row=0, column=0, columnspan=4, sticky="w", padx=15, pady=(12, 10))

        # Folder Selection Row
        ttk.Label(sec1_frame, text="Target Folder:", style="Card.TLabel").grid(row=1, column=0, sticky="w", padx=15, pady=8)
        
        self.path_var = tk.StringVar(value=str(Path.home()))
        path_entry = ttk.Entry(sec1_frame, textvariable=self.path_var, font=("Segoe UI", 10))
        path_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=8)

        btn_browse = ttk.Button(sec1_frame, text="Browse...", command=self.browse_folder)
        btn_browse.grid(row=1, column=2, padx=5, pady=8)

        # Minimum Size Filter
        ttk.Label(sec1_frame, text="Min Size (MB):", style="Card.TLabel").grid(row=1, column=3, sticky="e", padx=(15, 5), pady=8)
        
        self.minsize_var = tk.StringVar(value="50")
        minsize_spin = ttk.Spinbox(sec1_frame, from_=1, to=10000, textvariable=self.minsize_var, width=8)
        minsize_spin.grid(row=1, column=4, padx=5, pady=8)

        # Scan Action Button
        self.btn_scan = ttk.Button(sec1_frame, text="Start Deep Scan", style="Accent.TButton", command=self.start_scan_thread)
        self.btn_scan.grid(row=1, column=5, padx=15, pady=8)

        # Status Bar inside Section 1
        self.status_var = tk.StringVar(value="Ready to scan.")
        lbl_status = ttk.Label(sec1_frame, textvariable=self.status_var, style="Secondary.TLabel")
        lbl_status.grid(row=2, column=0, columnspan=6, sticky="w", padx=15, pady=(0, 12))

        # ==========================================
        # LOWER CONTAINER (Sections 2 & 3 Split)
        # ==========================================
        lower_container = ttk.Frame(self.root)
        lower_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        lower_container.rowconfigure(0, weight=1)
        lower_container.columnconfigure(0, weight=4) # Section 2
        lower_container.columnconfigure(1, weight=6) # Section 3

        # ==========================================
        # SECTION 2: Analytics & File Type Chart
        # ==========================================
        sec2_frame = ttk.Frame(lower_container, style="Card.TFrame")
        sec2_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        sec2_frame.rowconfigure(1, weight=1)
        sec2_frame.rowconfigure(2, weight=1)
        sec2_frame.columnconfigure(0, weight=1)

        ttk.Label(sec2_frame, text="Storage Breakdown by Type", font=("Segoe UI", 11, "bold"), style="Card.TLabel").grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))

        # Matplotlib Donut Chart Container
        self.chart_frame = ttk.Frame(sec2_frame, style="Card.TFrame")
        self.chart_frame.grid(row=1, column=0, sticky="nsew", padx=10)
        self.setup_placeholder_chart()

        # Breakdown List Table below chart
        breakdown_columns = ("category", "size", "percent")
        self.breakdown_tree = ttk.Treeview(sec2_frame, columns=breakdown_columns, show="headings", height=6)
        self.breakdown_tree.heading("category", text="File Category")
        self.breakdown_tree.heading("size", text="Total Size")
        self.breakdown_tree.heading("percent", text="Share (%)")
        
        self.breakdown_tree.column("category", width=120, anchor="w")
        self.breakdown_tree.column("size", width=100, anchor="e")
        self.breakdown_tree.column("percent", width=80, anchor="e")
        
        self.breakdown_tree.grid(row=2, column=0, sticky="nsew", padx=15, pady=15)

        # ==========================================
        # SECTION 3: Large Files Explorer List
        # ==========================================
        sec3_frame = ttk.Frame(lower_container, style="Card.TFrame")
        sec3_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        sec3_frame.rowconfigure(1, weight=1)
        sec3_frame.columnconfigure(0, weight=1)

        top_sec3 = ttk.Frame(sec3_frame, style="Card.TFrame")
        top_sec3.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
        top_sec3.columnconfigure(0, weight=1)

        ttk.Label(top_sec3, text="Discovered Large Files (Double-click to open)", font=("Segoe UI", 11, "bold"), style="Card.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(top_sec3, text="💡 Double-click any row to open its folder location", style="Secondary.TLabel").grid(row=1, column=0, sticky="w", pady=(2, 0))

        # Files Treeview
        files_columns = ("name", "size", "path")
        self.files_tree = ttk.Treeview(sec3_frame, columns=files_columns, show="headings")
        self.files_tree.heading("name", text="File Name")
        self.files_tree.heading("size", text="Size")
        self.files_tree.heading("path", text="Storage Location / Path")

        self.files_tree.column("name", width=180, anchor="w")
        self.files_tree.column("size", width=90, anchor="e")
        self.files_tree.column("path", width=340, anchor="w")

        self.files_tree.grid(row=1, column=0, sticky="nsew", padx=15, pady=15)

        # Scrollbar for Files Tree
        files_scroll = ttk.Scrollbar(sec3_frame, orient="vertical", command=self.files_tree.yview)
        self.files_tree.configure(yscrollcommand=files_scroll.set)
        
        # Bind double click action to open folder location
        self.files_tree.bind("<Double-1>", self.on_file_double_click)

    def setup_placeholder_chart(self):
        """Creates an empty placeholder chart on startup."""
        fig = Figure(figsize=(4, 3), dpi=100)
        fig.patch.set_facecolor(CARD_BG)
        ax = fig.add_subplot(111)
        ax.set_facecolor(CARD_BG)
        ax.text(0.5, 0.5, "No Data Scanned Yet", color=TEXT_SECONDARY, ha="center", va="center", fontsize=10)
        ax.axis('off')

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.current_canvas = canvas

    def browse_folder(self):
        """Opens folder dialog to choose target directory."""
        selected_dir = filedialog.askdirectory(initialdir=self.path_var.get())
        if selected_dir:
            self.path_var.set(selected_dir)

    def start_scan_thread(self):
        """Spawns background worker thread to execute the file scan."""
        target_path = self.path_var.get()
        if not os.path.exists(target_path):
            messagebox.showerror("Error", "The specified folder path does not exist.")
            return

        try:
            min_mb = float(self.minsize_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for minimum file size.")
            return

        min_bytes = int(min_mb * 1024 * 1024)

        # Lock UI controls during scan
        self.btn_scan.config(state="disabled")
        self.status_var.set("Scanning storage... Please wait.")
        
        # Clear previous results
        for row in self.files_tree.get_children():
            self.files_tree.delete(row)
        for row in self.breakdown_tree.get_children():
            self.breakdown_tree.delete(row)

        # Run scanner in thread
        threading.Thread(target=self.run_scanner, args=(target_path, min_bytes), daemon=True).start()

    def run_scanner(self, root_dir, min_bytes):
        """Scans directory recursively and aggregates file statistics."""
        scanned_files = []
        category_sizes = {cat: 0 for cat in EXT_CATEGORIES}
        category_sizes["Others"] = 0
        total_size = 0

        try:
            for dirpath, _, filenames in os.walk(root_dir):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        if os.path.islink(filepath):
                            continue
                        file_size = os.path.getsize(filepath)
                        
                        if file_size >= min_bytes:
                            total_size += file_size
                            
                            ext = Path(filename).suffix.lower()
                            matched_cat = "Others"
                            for cat, exts in EXT_CATEGORIES.items():
                                if ext in exts:
                                    matched_cat = cat
                                    break
                            
                            category_sizes[matched_cat] += file_size
                            scanned_files.append({
                                "name": filename,
                                "size": file_size,
                                "path": filepath,
                                "category": matched_cat
                            })
                    except (PermissionError, FileNotFoundError):
                        continue
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Scan Error", str(e)))

        # Sort files by size descending (largest first)
        scanned_files.sort(key=lambda x: x["size"], reverse=True)

        # Push results back to main UI thread
        self.root.after(0, lambda: self.update_ui_results(scanned_files, category_sizes, total_size))

    def update_ui_results(self, files, categories, total_size):
        """Updates UI elements with scan results."""
        self.scanned_files = files
        self.total_scanned_size = total_size
        self.btn_scan.config(state="normal")
        self.status_var.set(f"Scan complete. Found {len(files)} large files (Total: {format_size(total_size)})")

        for file in files:
            self.files_tree.insert("", "end", values=(file["name"], format_size(file["size"]), file["path"]))

        active_categories = {k: v for k, v in categories.items() if v > 0}
        
        for cat, size in sorted(active_categories.items(), key=lambda item: item[1], reverse=True):
            percent = (size / total_size * 100) if total_size > 0 else 0
            self.breakdown_tree.insert("", "end", values=(cat, format_size(size), f"{percent:.1f}%"))

        self.render_chart(active_categories, total_size)

    def render_chart(self, categories, total_size):
        """Renders modern matplotlib donut chart."""
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        fig = Figure(figsize=(4, 3), dpi=100)
        fig.patch.set_facecolor(CARD_BG)
        ax = fig.add_subplot(111)
        ax.set_facecolor(CARD_BG)

        if total_size == 0 or not categories:
            ax.text(0.5, 0.5, "No files matched criteria", color=TEXT_SECONDARY, ha="center", va="center", fontsize=10)
            ax.axis('off')
        else:
            labels = list(categories.keys())
            sizes = list(categories.values())
            colors = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#64748b"]

            wedges, texts, autotexts = ax.pie(
                sizes, 
                labels=labels, 
                autopct=lambda p: f'{p:.1f}%' if p > 3 else '', 
                startangle=140,
                colors=colors[:len(labels)],
                pctdistance=0.75,
                textprops=dict(color=TEXT_PRIMARY, fontsize=8)
            )
            
            for t in texts:
                t.set_color(TEXT_PRIMARY)
                t.set_fontsize(8)

            centre_circle = plt.Circle((0,0), 0.50, fc=CARD_BG)
            fig.gca().add_artist(centre_circle)
            ax.axis('equal')

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.current_canvas = canvas

    def on_file_double_click(self, event):
        """Opens the selected file's parent folder in the OS file explorer when double-clicked."""
        selected_item = self.files_tree.selection()
        if not selected_item:
            return

        item_values = self.files_tree.item(selected_item, "values")
        file_path = item_values[2]
        folder_path = os.path.dirname(file_path)

        if os.path.exists(folder_path):
            self.open_path_in_explorer(folder_path)
        else:
            messagebox.showwarning("Warning", "The folder path could not be found.")

    def open_path_in_explorer(self, path):
        """Cross-platform folder launcher."""
        try:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":
                subprocess.run(["open", path])
            else:
                subprocess.run(["xdg-open", path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open directory: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = StorageAnalyzerApp(root)
    root.mainloop()