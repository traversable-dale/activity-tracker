# Activity Tracker
### Cross-Platform Activity Monitor

**Version 0.2.0** | Updated February 14, 2026

A lightweight desktop app that tracks keyboard and mouse activity by application. Analyze your computer usage patterns with detailed reports.

![ref app](ref/ref-GUI.png)

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

## Building Standalone App (macOS)

```bash
# Install py2app
pip3.11 install py2app --break-system-packages

# Build (alias mode - recommended)
python3.11 setup.py py2app -A

# Move to Applications
mv dist/Activity\ Tracker.app /Applications/
```

**First launch:** Right-click → Open (to bypass security prompt)

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

## Credits

Built by Claude & Traversable Dale (2025)

**License:** Free for personal and educational use

---

**Happy Tracking! 🎯**
