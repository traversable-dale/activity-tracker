# Activity Tracker

**Version 0.2.0** | Cross-Platform Activity Monitor

A lightweight desktop app that tracks keyboard and mouse activity by application. Analyze your computer usage patterns with detailed reports.

![ref app](ref/ref-GUI.png)

---

## Deployment Options

| Method | Platform | Best For | Installation |
|--------|----------|----------|--------------|
| **Python Script** | macOS/Windows | Development, integration | `pip install` + `python activity_tracker.py` |
| **macOS .app** | macOS only | Mac users, no terminal | `py2app` build → double-click |
| **Windows .exe** | Windows only | Quick distribution | `pyinstaller` build → double-click |
| **Windows Installer** | Windows only | Professional deployment | Inno Setup wizard install |

---

## Quick Start

### macOS

```bash
# Install Python 3.11 and dependencies
brew install python@3.11 python-tk@3.11
pip3.11 install pynput pillow --break-system-packages

# Run the app
python3.11 activity_tracker.py
```

**Grant permissions:** System Preferences → Security & Privacy → Accessibility + Input Monitoring → Add Python 3.11

### Windows

```bash
# Install dependencies
pip install pynput pillow pywin32 psutil

# Run the app
python activity_tracker.py
```

No special permissions needed!

---

### Command Line Options

Run from terminal with custom settings:

```bash
# macOS
python3.11 activity_tracker.py

# Windows  
python activity_tracker.py
```

**To run in background (no GUI):**
Modify the script to skip `ActivityTrackerGUI()` and just run `ActivityTracker()` directly.

---

## Building Standalone Apps

> **Windows Users:** See [WINDOWS_BUILD.md](WINDOWS_BUILD.md) for detailed Windows build instructions.

---

### macOS App Bundle

Create a double-clickable `.app` that runs without Terminal:

```bash
# Install py2app
pip3.11 install py2app --break-system-packages

# Build (alias mode - recommended for development)
python3.11 setup.py py2app -A

# Or build full bundle (for distribution)
python3.11 setup.py py2app

# Move to Applications
mv dist/Activity\ Tracker.app /Applications/
```

**First launch:** Right-click → Open (to bypass security prompt)

**Note:** Alias mode (`-A`) creates a lightweight app that links to your source files - faster builds, instant updates when you edit code. Full bundle packages everything inside the app.

---

### Windows Executable

Create a double-clickable `.exe` installer:

#### Quick Build (Using Spec Files)

```bash
# Install PyInstaller
pip install pyinstaller

# Option 1: Single-file executable (easiest to share)
pyinstaller ActivityTracker-onefile.spec

# Option 2: Folder mode (faster startup)
pyinstaller ActivityTracker.spec

# The .exe will be in dist/ folder
```

#### Manual Build (Without Spec Files)

```bash
# Single-file executable
pyinstaller --onefile --windowed --name "ActivityTracker" ^
            --icon=ref/TDT-logo-white-circle.ico activity_tracker.py

# Or folder mode
pyinstaller --windowed --name "ActivityTracker" ^
            --icon=ref/TDT-logo-white-circle.ico activity_tracker.py
```

---

---

## Professional Installer with GUI Wizard

For a full installation experience like commercial software:

1. **Build the .exe** first using PyInstaller (folder mode recommended)
   ```bash
   pyinstaller ActivityTracker.spec
   ```

2. **Download Inno Setup** (free): https://jrsoftware.org/isinfo.php

3. **Open `installer-setup.iss`** in Inno Setup

4. **Click "Compile"** - creates `Activity_Tracker_Setup.exe` in `Output/` folder

5. **Distribute** the setup file - users get a professional install wizard!

**The installer provides:**
- Installation wizard with progress bar
- Desktop shortcut option
- Start menu entry
- Proper uninstaller
- Professional look and feel

**Note:** 
- `--onefile` = single `.exe` (slower startup, easier to share)
- Folder mode = faster startup, better for installer distribution
- Spec files include the background image automatically

---

## What It Does

- **Tracks** every keystroke and mouse click
- **Records** which application you're using
- **Saves** everything to CSV files for analysis
- **Generates** detailed reports with stats and timelines
- **Privacy-safe** - keystroke categories only, no raw text capture

### Features

- **Simple GUI** - Compact 320x120 window with PAUSE, SUMMARY, FOLDER buttons
- **Auto-save** - Events saved every 30 seconds
- **Analytics** - WPM, CPM, work periods, breaks, time per app
- **Reports** - Export to TXT and CSV formats
- **100% Offline** - All data stays on your computer
- **Customizable** - Colors, fonts, window size (edit settings at top of script)

---

## Usage

### Interface

```
┌──────────────────────────────────────┐
│           TRACKING                   │
│                                      │
│  [PAUSE]  [SUMMARY]  [FOLDER]       │
│                                      │
│       2m 30s | 145 events            │
└──────────────────────────────────────┘
```

- **PAUSE/RESUME** - Temporarily stop recording (for privacy)
- **SUMMARY** - Generate analytics report (TXT + CSV)
- **FOLDER** - Open data directory

### Data Output

CSV files saved to `activity_data/`:

```csv
timestamp,app,event_type,key
2026-02-14T15:35:00.123456,chrome.exe,keystroke,char
2026-02-14T15:35:00.234567,chrome.exe,keystroke,separator
2026-02-14T15:35:00.345678,chrome.exe,click,left
```

Reports saved to `activity_data/reports/`:
- `summary_YYYYMMDD_HHMMSS.txt` - Human-readable
- `summary_YYYYMMDD_HHMMSS.csv` - Machine-readable (for TouchDesigner, etc.)

---

## Advanced Usage

### Running from Python (for integration)

You can import and control the tracker programmatically from other Python scripts:

```python
# Import the tracker
from activity_tracker import ActivityTracker

# Create tracker instance
tracker = ActivityTracker(autosave_interval=30)

# Start tracking
tracker.start_tracking()

# Later: pause temporarily
tracker.pause_tracking()

# Resume
tracker.resume_tracking()

# Stop and save
tracker.stop_tracking()

# Access data
events = tracker.load_all_sessions()
```

**Use cases:**
- Start/stop tracking from another Python app
- Integrate with TouchDesigner using Python DATs
- Build custom dashboards that control the tracker
- Schedule tracking sessions programmatically

---


---

## Privacy & Security

### What Gets Recorded
✅ Keystroke categories (char/separator/modifier)  
✅ Mouse clicks (which button)  
✅ Application names  
✅ Timestamps  

❌ No screenshots or screen content  
❌ No cursor positions  
❌ No window titles or URLs  
❌ No raw text (what you actually typed)  

All data stored locally. No internet connection required.

---

## Customization

Edit settings at top of `activity_tracker.py`:

```python
# Window
WINDOW_SIZE = "320x120"

# Colors
BG_COLOR = "#FFFFFF"
BUTTON_PAUSE_BG = "#9C2D2D"
STATUS_TRACKING_COLOR = "#FFFFFF"

# Fonts
FONT_FAMILY = "Arial"
FONT_SIZE_STATUS = 10

# Auto-save interval
autosave_interval=30  # seconds
```

---

## Troubleshooting

**Module not found error**
```bash
# macOS
pip3.11 install pynput pillow --break-system-packages

# Windows
pip install pynput pillow pywin32 psutil
```

**macOS: Keyboard not tracking**
- Grant Accessibility + Input Monitoring permissions in System Preferences
- Use Python 3.11 (NOT 3.14 - compatibility issues)
- Keyboard listener may show an error but still work (known macOS issue)

**Windows: No events recorded**
- Make sure app shows "TRACKING" status
- Check terminal for event logs

---

## Technical Details

- **Language:** Python 3.11
- **GUI:** Tkinter
- **Input Monitoring:** pynput
- **Performance:** ~20-30 MB RAM, <1% CPU idle
- **Storage:** ~1 MB per 8-hour workday

### Use Cases
- Track daily computer usage patterns
- Measure typing speed (WPM) and activity levels
- Analyze time spent per application
- Export data for analysis in Excel, Python, R, TouchDesigner
- Build custom activity dashboards

---

# Credits & Terms

>#### TERMS OF TEMPORAL INTERACTION:
>##### Your engagement with this codebase constitutes acceptance of the following metaphysical obligations: 
>###### (1) Each click and keystroke is an invocation of causality itself; (2) Tracking constitutes witnessing, and witnessing constitutes participation in the inexorable forward march of entropy; (3) User acknowledges that time spent debugging is time that can never be recovered and has significant ontological implications; (4) By scrolling, User enters the river of becoming and cannot step in the same code twice.


 ###### **Copyright:** good luck.


 ###### Built by Claude & Traversable Dale

###### Traversable Dale Technologies (2025)

---

**License:** Free for personal and educational use

---

**Happy Tracking! 🎯**