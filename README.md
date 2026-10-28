# StellarStorage Analyzer 🚀

> **A modern, high-performance, dark-themed desktop disk space analyzer built with Python, Tkinter, and Matplotlib.**

---

## 📊 Badges

---

## 📑 Table of Contents

1. [Description](https://www.google.com/search?q=%23-description)
2. [Features](https://www.google.com/search?q=%23-features)
3. [Folder Structure Diagram](https://www.google.com/search?q=%23-folder-structure-diagram)
4. [Data Flow Diagram (DFD)](https://www.google.com/search?q=%23-data-flow-diagram-dfd)
5. [Entity-Relationship (ER) Diagram](https://www.google.com/search?q=%23-entity-relationship-er-diagram)
6. [Installation](https://www.google.com/search?q=%23-installation)
7. [Setup Guide](https://www.google.com/search?q=%23-setup-guide)
8. [Usage Guide](https://www.google.com/search?q=%23-usage-guide)
9. [Use Cases](https://www.google.com/search?q=%23-use-cases)
10. [Pros and Cons](https://www.google.com/search?q=%23-pros-and-cons)
11. [Limitations](https://www.google.com/search?q=%23-limitations)
12. [Bugs and Vulnerabilities](https://www.google.com/search?q=%23-bugs-and-vulnerabilities)
13. [Future Updates](https://www.google.com/search?q=%23-future-updates)
14. [Contributing](https://www.google.com/search?q=%23-contributing)
15. [Like, Share, Star](https://www.google.com/search?q=%23-like-share-star)
16. [Thanks & Acknowledgements](https://www.google.com/search?q=%23-thanks--acknowledgements)

---

## 📝 Description

**StellarStorage Analyzer** is a desktop utility designed to help users quickly discover what is consuming their hard drive storage. Powered by Python's core `os` and `threading` modules, it scans target drives or folders recursively, filters files by user-defined size thresholds, categorizes them by type (Videos, Images, Documents, Archives, Audio, Code), visualizes storage distribution using a dynamic Matplotlib Donut chart, and allows instant file location navigation with a simple double-click.

---

## ✨ Features

* **Asynchronous Multithreaded Scanning:** Runs disk traversal on a background worker thread to ensure the UI never freezes or locks up.
* **Modern Dark-Themed UI:** Crafted with custom `ttk` styling, slate color palettes, and polished layout geometry.
* **Interactive Donut Chart:** Visualizes storage consumption breakdown by file categories in real time.
* **Configurable Size Filter:** Dynamically set a minimum file size threshold (e.g., find all files larger than 50 MB).
* **Instant Explorer Integration:** Double-clicking any discovered large file instantly opens its parent folder location in Windows Explorer, macOS Finder, or Linux file managers.

---

## 📂 Folder Structure Diagram

```text
StellarStorage/
│
├── disk_analyzer.py        # Main application script
├── README.md               # Project documentation
└── assets/                 # Optional images, icons, and themes
    └── preview.png         # UI screenshot preview

```

---

## 🔄 Data Flow Diagram (DFD)

The diagram below outlines how data flows through the application from user input to final UI rendering:

```text
 [ User Input ] 
   │ (Selects Folder & Min Size)
   ▼
 [ Control Panel (GUI) ] ──(Spawns Thread)──► [ Background Scanner Thread ]
                                                     │
                                            (Walks OS Directory)
                                                     │
                                           [ OS File System (os.walk) ]
                                                     │
                                            (Returns file sizes & paths)
                                                     │
                                                     ▼
 [ Main UI Thread ] ◄──(Marshals via root.after)── [ Data Aggregator ]
   │                                                 │
   ├─► Populates Files Treeview                      ├─► Calculates Category Shares
   ├─► Populates Breakdown Table                     └─► Renders Donut Chart (Matplotlib)
   ▼
 [ Interactive GUI Display ]
   │ (Double-click file row)
   ▼
 [ OS File Explorer Launch ]

```

---

## 📐 Entity-Relationship (ER) / In-Memory Data Model

Since StellarStorage processes file system nodes in-memory rather than querying an external database, the logical object relationship is structured as follows:

```text
┌─────────────────────────┐          1:N          ┌─────────────────────────┐
│     Target Directory    │ ────────────────────> │        File Item        │
├─────────────────────────┤                       ├─────────────────────────┤
│ - Root Path             │                       │ - Name: String          │
│ - Scan Parameters       │                       │ - Size: Integer (Bytes) │
└─────────────────────────┘                       │ - Path: String          │
                                                  │ - Category: String      │
                                                  └─────────────────────────┘
                                                               │
                                                               │ N:1 Aggregation
                                                               ▼
                                                  ┌─────────────────────────┤
                                                  │    File Category Stat   │
                                                  ├─────────────────────────┤
                                                  │ - Category Name         │
                                                  │ - Total Size            │
                                                  │ - Percentage Share      │
                                                  └─────────────────────────┘

```

---

## 📦 Installation

Ensure you have **Python 3.8+** installed on your machine.

1. Clone or download this repository.
2. Open your terminal or command prompt in the project directory.
3. Install the required plotting dependency (`matplotlib`):
```bash
pip install matplotlib

```



---

## ⚙️ Setup Guide

1. Save the application script as `disk_analyzer.py`.
2. Verify that Python and `matplotlib` are correctly configured by running:
```bash
python -c "import matplotlib; print('Matplotlib ready!')"

```



---

## 💻 Usage

1. Launch the application from your terminal:
```bash
python disk_analyzer.py

```


2. **Section 1 (Control Panel):**
* Click **Browse...** to select the target drive or folder you want to audit.
* Enter your **Min Size (MB)** threshold (e.g., `50` to find files $\ge$ 50MB).
* Click **Start Deep Scan**.


3. **Section 2 (Analytics & Chart):**
* View the dynamic percentage breakdown Donut chart and category table.


4. **Section 3 (Large Files Explorer):**
* Review discovered files sorted from largest to smallest.
* **Double-click** any file row to instantly open its storage folder.



---

## ⚖️ Pros and Cons

### Pros

* **Zero Lag:** Asynchronous thread architecture keeps the desktop interface smooth.
* **Zero External DB Required:** Operates entirely client-side using native Python modules.
* **Cross-Platform:** Works seamlessly on Windows, macOS, and Linux.
* **Actionable Cleanup:** Direct folder navigation eliminates friction when deleting unwanted files.

### Cons

* **Single-Pass Scan:** Does not cache scan results; requires a fresh scan if files are modified outside the app.
* **File System Permissions:** System-locked files or restricted directories may trigger `PermissionError` (handled gracefully by skipping).

---

## ⚠️ Limitations

* Scanning extremely large directories (e.g., entire multi-terabyte drives with millions of tiny files) can take several minutes depending on disk read speeds (HDD vs SSD).
* Requires user read permissions for nested subfolders.

---

## 🎯 Use Cases

* **Developer Workflows:** Quickly locating and purging hidden `node_modules`, Python virtual environments (`.venv`), or build artifacts hogging disk space.
* **Media Management:** Finding forgotten 4K video files, raw camera images, or large ISO archives.
* **General Storage Audits:** Freeing up critical SSD space on laptops running low on capacity.

---

## 🐛 Bugs and Vulnerabilities

* **Access Denied Handlers:** Handled via try-except blocks (`PermissionError`, `FileNotFoundError`) to prevent application crashes during recursive file walking.
* **Known Consideration:** Operating systems may lock files currently in active use by other applications; their size will not be counted if read access is denied.

---

## 🚀 Future Updates

* [ ] **Export Reports:** Export scan logs to CSV or JSON formats.
* [ ] **Interactive Drill-Down:** Click chart slices to filter sub-folders directly.
* [ ] **Theme Switcher:** Toggle between Dark and Light modern themes.
* [ ] **Direct Deletion Tool:** Secure file shredding or moving straight to the OS Recycle Bin / Trash.

---

## 👥 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page or submit a pull request.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git origin push feature/AmazingFeature`)
5. Open a Pull Request

---

## ⭐ Like, Share, Star!

If this project helped you reclaim precious storage space on your computer, please **give it a ⭐ star** on GitHub and share it with fellow developers!

---

## 🙏 Thanks & Acknowledgements

* Built with Python's robust standard library (`os`, `threading`, `tkinter`).
* Chart visualizations powered by the open-source **Matplotlib** community.