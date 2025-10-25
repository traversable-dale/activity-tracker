# Activity Tracker

A lightweight, cross-platform desktop application that monitors your keyboard and mouse activity in real-time.

Track every keystroke and click, see which applications you use most, and analyze your computer usage patterns over time.

---

## Table of Contents

- [What It Does](#what-it-does)
- [Key Features](#key-features)
- [Installation](#installation)
- [Building a Standalone App (Optional)](#building-a-standalone-app-optional)
- [How to Use](#how-to-use)
- [Data Format](#data-format)
- [Use Cases](#use-cases)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)
- [Privacy & Security](#privacy--security)
- [Technical Details](#technical-details)
- [How It Works: Code Breakdown](#how-it-works-code-breakdown)
- [FAQ](#faq)
- [Credits](#credits)
- [License](#license)

---

![ref app](ref/ref-GUI.png)

## What It Does

**Activity Tracker** runs quietly in the background and records:

- **Every keystroke** you type
- **Every mouse click** you make (left, right, middle)
- **Which application** you're using when each event happens
- **Precise timestamps** for every action

All data is saved locally to CSV files that you can analyze later.

---

## Key Features

### **Simple & Minimal**
- Clean black and white interface
- Compact 320x120 window
- Clock + Event counter
- Three buttons: 
  - STOP/START | activate / de-activated tracking
  - APP/GLOBAL | switch between app-specific / global tracking
  - FOLDER | open folder containing saved data

### **Smart Data Collection**
- Tracks by application OR globally
- Auto-saves every 60 seconds
- Session-based storage (one file per session)
- CSV format for easy analysis (~50% smaller than JSON!)

### **Privacy First**
- No cursor position tracking
- No screenshots or screen content
- 100% offline - no internet connection
- All data stays on your computer

### **Customizable**
- Edit colors at top of script
- Change fonts and sizes
- Adjust window dimensions
- Set auto-save interval

---

## Installation

### Requirements

- **macOS** (Windows/Linux compatible with minor tweaks)
- **Python 3.11** ⚠️ **Important: Must use 3.11, NOT 3.14!**
- **Homebrew** (for macOS dependencies)

### Step 1: Install Python 3.11

```bash
# Uninstall Python 3.14 if you have it
brew uninstall python@3.14

# Install Python 3.11 (required for compatibility)
brew install python@3.11

# Install python-tk for 3.11
brew install python-tk@3.11
```

**Why Python 3.11?** Python 3.14 is too new and has compatibility issues with pynput. Python 3.11 is the stable, tested version that works perfectly.

### Step 2: Install Python Packages

```bash
pip3.11 install pynput pillow --break-system-packages
```

**Note:** The `--break-system-packages` flag is safe for local projects like this.

### Step 3: Download the Script

Save `activity_tracker.py` to a folder on your computer.

### Step 4: Grant Permissions (macOS Only)

The app needs permission to monitor keyboard and mouse:

1. Run the app once: `python3.11 activity_tracker.py`
2. Go to **System Preferences** → **Security & Privacy** → **Privacy**
3. Select **Accessibility** from the left sidebar
4. Click the lock 🔒 and enter your password
5. Click **+** and add Python 3.11:
   - Press **Cmd + Shift + G**
   - Paste: `/opt/homebrew/Cellar/python@3.11/3.11.14/Frameworks/Python.framework/Versions/3.11/Resources/Python.app`
   - Click **Open**
6. Check the box ✓ next to Python
7. Do the same for **Input Monitoring**
8. Restart the app

---

## Building a Standalone App (Optional)

Want to run Activity Tracker as a double-clickable macOS app without opening Terminal? Follow these steps to build a standalone `.app` bundle.

### Requirements

- Everything from the Installation section above
- **py2app** package for building macOS apps

### Step 1: Install py2app and All Dependencies

```bash
pip3.11 install py2app macholib modulegraph altgraph --break-system-packages
```

**Note:** py2app requires several dependencies (`macholib`, `modulegraph`, `altgraph`). Installing them all together prevents cascading dependency errors during the build.

### Step 2: Build the App

Navigate to the folder containing `activity_tracker.py` and `setup.py`:

**Option A: Alias Mode (Recommended)**

```bash
cd /path/to/tracker
python3.11 setup.py py2app -A
```

Alias mode creates a lightweight app that links to your source files. This is faster, more reliable, and easier to debug.

**Option B: Full Bundle**

```bash
cd /path/to/tracker
python3.11 setup.py py2app
```

Full bundle mode packages everything into the app. Use this if you want to share the app or move it away from the source folder.

Both commands will:
- Create a `build/` folder (temporary files)
- Create a `dist/` folder containing **Activity Tracker.app**

### Step 3: Move the App

```bash
# Move the app to your Applications folder
mv dist/Activity\ Tracker.app /Applications/

# Or open the dist folder to drag it manually
open dist/
```

### Step 4: First Launch

1. Open **Finder** and go to **Applications**
2. Find **Activity Tracker.app**
3. **Right-click** (or Ctrl+click) and select **Open**
4. Click **Open** in the security dialog (first launch only)

macOS will ask for accessibility permissions just like running from Terminal. Follow the permission steps from the Installation section above.

### Using the Standalone App

Once built and moved to Applications:

- **Double-click** to launch (no Terminal needed!)
- The app runs identically to the Python script
- Data still saves to `activity_data/` in the same folder
- Click FOLDER button to open the data directory

### Cleaning Up Build Files

After building, you can delete the temporary files:

```bash
cd /path/to/tracker
rm -rf build/ dist/
```

Keep `setup.py` if you want to rebuild in the future.

### Rebuilding After Code Changes

If you modify `activity_tracker.py`:

**For alias mode builds:**
```bash
# Just rebuild - changes are automatically reflected!
python3.11 setup.py py2app -A
```

**For full bundle builds:**
```bash
# Clean old build
rm -rf build/ dist/

# Rebuild
python3.11 setup.py py2app

# Move new version
mv dist/Activity\ Tracker.app /Applications/
```

**Note:** With alias mode, the app links to your source files, so code changes take effect immediately without rebuilding!

### Troubleshooting

**Missing py2app dependencies**
```
pkg_resources.DistributionNotFound: The 'macholib>=1.16.2' distribution was not found
pkg_resources.DistributionNotFound: The 'modulegraph>=0.19.6' distribution was not found
```
- Install all dependencies at once: `pip3.11 install py2app macholib modulegraph altgraph --break-system-packages`
- Then rebuild: `python3.11 setup.py py2app -A`
- **Tip:** If you see multiple "distribution not found" errors, just install all the missing packages together

**setuptools deprecation warnings**
- You may see warnings about `setuptools.installer` and `pkg_resources` being deprecated
- These are harmless warnings from py2app and won't affect the build
- The app will still build and run correctly

**"Activity Tracker.app" is damaged and can't be opened**
- This happens when macOS can't verify the app
- Right-click → Open instead of double-clicking
- Or run: `xattr -cr /Applications/Activity\ Tracker.app`

**App doesn't start / crashes immediately**
- Check that you built with Python 3.11 (not 3.14)
- Verify all dependencies are installed
- Try running the Python script directly to see error messages

**Data folder not found**
- The app creates `activity_data/` relative to where it's located
- When in Applications, this will be `/Applications/activity_data/`
- Consider modifying the script to use a fixed home directory path

---





## How to Use

### Starting the Tracker

```bash
cd /path/to/tracker
python3.11 activity_tracker.py
```

The app will:
- Open a small window
- Start tracking immediately
- Print each event to the terminal
- Auto-save every 60 seconds

### The Interface

```
┌─────────────────────────┐
│      TRACKING           │
│                         │
│  [STOP] [APP] [FOLDER]  │
│                         │
│   2m 30s | 145 events   │
└─────────────────────────┘
```

**STOP/START** - Toggle tracking on/off

**APP/GLOBAL** - Switch modes:
- **APP mode**: Track which application each event belongs to
- **GLOBAL mode**: Track all events without app names

**FOLDER** - Opens the `activity_data` folder in Finder

**Important:** The listeners run continuously in the background. When you click STOP, it saves the current session but keeps monitoring. When you click START, it begins a new session.

### Reading the Data

All sessions are saved as CSV files in the `activity_data/` folder:

```
activity_data/
  ├── session_20251023_143500.csv
  ├── session_20251023_150200.csv
  └── session_20251023_152700.csv
```

Each CSV file contains:

```csv
timestamp,app,event_type,key
2025-10-23T15:35:00.123456,Chrome,keystroke,h
2025-10-23T15:35:00.234567,Chrome,keystroke,e
2025-10-23T15:35:00.345678,Chrome,click,left
```

### Terminal Output

Clean, one-line-per-event format:

```
Activity Tracker Started
========================================
Tracking started... Session ID: 20251023_143500
Creating listeners for the first time...
✓ Keyboard listener started
✓ Mouse listener started
[Chrome] keystroke: h
[Chrome] keystroke: e
[Chrome] keystroke: l
[Chrome] click: left
>>> Auto-saved: 245 events | File: activity_data/session_20251023_143500.csv <<<
```

---





## Data Format

### CSV Structure

| Column | Description | Example |
|--------|-------------|---------|
| `timestamp` | ISO 8601 timestamp | `2025-10-23T15:35:00.123456` |
| `app` | Application name | `Chrome`, `Finder`, `Global` |
| `event_type` | Type of event | `keystroke` or `click` |
| `key` | Specific key or button | `a`, `space`, `left`, `right` |

### File Naming

Files are named with session start time:

```
session_YYYYMMDD_HHMMSS.csv
        │       │
        │       └─ Hour, minute, second
        └───────── Year, month, day
```

### File Size

Approximate file sizes:

- **1 hour of light use**: ~50 KB
- **1 hour of heavy typing**: ~200 KB
- **8 hour work day**: ~500 KB - 1 MB

CSV format is 50% smaller than JSON!

---


## Use Cases

### Analytics + Productivity
- Track your daily computer usage patterns
- Measure typing speed and activity levels
- Measure time spent in different applications / see which apps you use most
- Track breaks and active periods / find your most productive hours

### Data Analysis Projects
- Import CSVs into Excel, Python, R
- Create visualizations and charts
- Build custom activity dashboards
- Train machine learning models

---

## Customization

### Changing Colors

Edit the settings at the top of `activity_tracker.py`:

```python
# Background
BG_COLOR = "#FFFFFF"  # White

# Button colors
BUTTON_STOP_BG = "#FFFFFF"  # White buttons
BUTTON_TEXT_COLOR = "#000000"  # Black text
BUTTON_BORDER_COLOR = "#000000"  # Black border

# Status colors
STATUS_TRACKING_COLOR = "#000000"  # Black
STATUS_STOPPED_COLOR = "#000000"  # Black
```

### Changing Window Size

```python
WINDOW_SIZE = "320x120"  # Width x Height
```

### Changing Auto-Save Interval

```python
self.tracker = ActivityTracker(autosave_interval=60)  # seconds
```

Change `60` to any number of seconds.

### Changing Fonts

```python
FONT_FAMILY = "Arial"
FONT_SIZE_STATUS = 10
FONT_SIZE_BUTTON = 9
```

---

## Troubleshooting

### "Module not found" error

Install dependencies with Python 3.11:
```bash
pip3.11 install pynput pillow --break-system-packages
```

### App crashes on startup

Make sure you have Python 3.11 AND python-tk:
```bash
brew install python@3.11
brew install python-tk@3.11
```

### Keyboard tracking not working

Common issue! The keyboard listener may show an error in the thread but still work. Check:

1. You're using Python 3.11 (not 3.14)
2. Python has **Accessibility** permissions
3. Python has **Input Monitoring** permissions
4. Run the app and type - events should appear even if there's an error message

If you see this error, it's usually fine:
```
Exception in thread Thread-2:
...
KeyError: 'AXIsProcessTrusted'
```

The keyboard listener still works despite the error!

### Start/Stop button crashes the app

This should be fixed in the current version. The listeners now run continuously in the background and don't restart.

### No events being recorded

Check that:
1. Status shows "TRACKING" (not "STOPPED")
2. You've granted system permissions
3. The terminal shows event lines
4. You're using Python 3.11

### "externally-managed-environment" error

Use the `--break-system-packages` flag:
```bash
pip3.11 install pynput pillow --break-system-packages
```

---

## Privacy & Security

### What Gets Recorded

✅ **YES** - Key presses (which key)

✅ **YES** - Mouse clicks (which button)

✅ **YES** - Application names

✅ **YES** - Timestamps

❌ **NO** - Screenshots or screen content

❌ **NO** - Cursor positions

❌ **NO** - Window titles or URLs

❌ **NO** - File paths or documents

### Data Storage

- All data stored **locally** on your computer
- No cloud sync or remote servers
- No internet connection required
- You control your own data
- Delete files anytime to remove data

### Permissions

The app requires system permissions to:
- Monitor keyboard input (Accessibility + Input Monitoring)
- Monitor mouse input (Accessibility)
- Get active application name

It does **NOT** require:
- Screen recording
- File system access (except its own folder)
- Network access
- Camera or microphone

---

## Technical Details

### Architecture

```
┌─────────────────────────────────────┐
│  GUI (Tkinter)                      │
│  - Display window                   │
│  - Update stats                     │
│  - Control buttons                  │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  ActivityTracker                    │
│  - Record events                    │
│  - Manage sessions                  │
│  - Save to CSV                      │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  Listeners (pynput)                 │
│  - Keyboard monitoring              │
│  - Mouse monitoring                 │
│  - Run continuously                 │
└─────────────────────────────────────┘
```

### Threading Model

- **Main Thread**: GUI and display updates
- **Keyboard Thread**: Monitors keyboard (runs continuously)
- **Mouse Thread**: Monitors mouse (runs continuously)
- **Tracking Thread**: Starts/stops recording (not listeners)

**Important:** Listeners run continuously. Stop/Start only controls whether events are recorded, not whether listeners are active.

### Performance

- **Memory**: ~20-30 MB RAM usage
- **CPU**: <1% when idle, 2-5% during heavy typing
- **Storage**: ~1 MB per 8-hour workday

### Known Issues

1. **Keyboard thread error on startup**: The keyboard listener may show a `KeyError: 'AXIsProcessTrusted'` error but will still work. This is a known pynput/macOS compatibility issue that doesn't affect functionality.

2. **Python 3.14 incompatibility**: pynput has breaking issues with Python 3.14. Always use Python 3.11.

3. **Listeners can't restart**: pynput listeners can't be stopped and restarted. This is why we keep them running continuously and just toggle the recording flag.

---

## How It Works: Code Breakdown

Want to understand what's happening under the hood? Here's a plain-language explanation of the code and libraries.

### The py2app Dependencies

When building the standalone app, py2app needs several helper libraries:

**altgraph**
- Creates and analyzes graph data structures (nodes and connections)
- Think of it like mapping relationships: "A connects to B, B connects to C"
- Used by the other tools to track relationships between code modules

**modulegraph**
- Analyzes your Python code to find ALL the modules/packages your app uses
- Follows the import chain: "You import X, X imports Y, Y imports Z..."
- Creates a complete dependency tree so py2app knows what to bundle
- Uses altgraph to store this tree structure

**macholib**
- Reads and modifies Mach-O files (the executable format on macOS)
- Mach-O = "Mach Object" (like .exe on Windows, but for macOS/iOS)
- Helps py2app understand compiled libraries and frameworks
- Fixes paths to dynamic libraries so they work inside the app bundle

**How they work together:**
1. `modulegraph` (using `altgraph`) finds all your Python dependencies
2. `macholib` handles the compiled/binary dependencies (C libraries, frameworks)
3. `py2app` uses both to package everything into a .app bundle

### Code Structure

The `activity_tracker.py` file has three main sections:

#### 1. Imports & Setup (Lines 1-76)

```python
import tkinter as tk  # GUI framework
from pynput import keyboard, mouse  # Listen to keyboard/mouse
from AppKit import NSWorkspace  # Get active app name (macOS)
```

- Loads all the tools needed
- Sets up customization variables (colors, fonts, window size)
- Imports macOS-specific frameworks for tracking which app is active

#### 2. ActivityTracker Class (Lines 79-252)

**The Core Tracking Engine**

`__init__()` - Initialization
- Creates the `activity_data/` folder
- Sets up variables to track sessions and events
- Prepares everything but doesn't start listeners yet

`get_active_application()` - Which app is the user in?
- Asks macOS "which app window is in front right now?"
- Uses NSWorkspace (macOS framework) to check the active window
- Returns app name like "Chrome" or "Finder"

`record_event()` - Save a keystroke or click
- Creates a timestamp (ISO 8601 format)
- Gets the active app name
- Adds event to a list
- Prints to terminal for immediate feedback
- Auto-saves to CSV every 60 seconds

`on_key_press()` & `on_click()` - Input callbacks
- pynput calls these functions automatically when input happens
- They extract the key/button info and pass it to `record_event()`

`start_tracking()` - Begin a new session
- Creates a unique session ID (timestamp: `20251025_143000`)
- Creates listeners if they don't exist yet (keyboard & mouse)
- Sets `self.tracking = True` so events get recorded

`stop_tracking()` - Pause recording
- Saves current session to CSV
- Sets `self.tracking = False`
- Note: listeners keep running in background, just don't record

`save_session()` - Write events to CSV file
- Opens/creates a CSV file in `activity_data/`
- Writes all events with columns: timestamp, app, event_type, key
- Clears the event list for the next batch

#### 3. GUI Class (Lines 288-496)

**The Visual Interface**

**Initialization:**
- Creates a small window (320x120 pixels)
- Loads background image if available, otherwise uses solid color
- Creates the ActivityTracker instance
- Starts tracking automatically on launch

**UI Components:**
```
┌─────────────────────┐
│    TRACKING         │  ← Status label
│                     │
│ [STOP] [APP] [FOLDER] │  ← Control buttons
│                     │
│  2m 30s | 145 events │  ← Stats label
└─────────────────────┘
```

**Button Functions:**

`toggle_tracking()` - STOP/START button
- Stops or starts recording (not the listeners!)
- Updates button text and status label color

`toggle_mode()` - APP/GLOBAL button
- Switches between tracking by app vs. tracking everything as "Global"

`open_data_folder()` - FOLDER button
- Opens the `activity_data/` folder in Finder

`update_status()` - Status display loop
- Updates every second
- Shows elapsed time and event count while tracking
- Shows total events when stopped
- Uses `self.root.after(1000, ...)` to create a repeating timer

### The Flow: What Happens When

**When you launch the app:**
1. Creates GUI window
2. Creates ActivityTracker instance
3. Starts tracking thread
4. Starts keyboard listener thread
5. Starts mouse listener thread
6. Begins status update loop

**When you type or click:**
1. pynput listener catches the event in its background thread
2. Calls `on_key_press()` or `on_click()`
3. Calls `record_event()` with the key/button info
4. Adds event to the session list
5. Prints to terminal for feedback
6. Every 60 seconds, auto-saves entire list to CSV

**When you click STOP:**
1. Sets `self.tracking = False`
2. Saves current session to CSV file
3. Listeners keep running (can't stop/restart them reliably)
4. Events are captured but ignored until you click START

**When you click START:**
1. Creates new session ID (new timestamp)
2. Sets `self.tracking = True`
3. Events start recording again to a new CSV file

**When you close the app:**
1. Calls `on_closing()`
2. Saves final session
3. Destroys GUI window
4. Listeners stop automatically (they're daemon threads)

### Key Design Decisions

**Why listeners run continuously:**
- pynput listeners can't be reliably stopped and restarted
- Solution: keep them running, use a boolean flag (`self.tracking`) to control recording
- STOP button = pause recording, START button = resume recording

**Why threading:**
- GUI needs the main thread to stay responsive
- Listeners need background threads to monitor input
- Status updates need a timer loop
- Without threading, the GUI would freeze waiting for input

**Why CSV instead of JSON:**
- Much smaller file size (~50% savings for large datasets)
- Easier to import into Excel, Pandas, R, or other analysis tools
- Simple tabular structure: one event per row
- Fast to write (append mode)

**Why auto-save every 60 seconds:**
- Prevents data loss if the app crashes
- Low overhead (CSV writes are fast)
- Customizable via `autosave_interval` parameter
- Keeps memory usage low by clearing the event list

**Why session-based files:**
- Each START creates a new file with unique timestamp
- Easy to analyze individual work sessions
- No risk of corrupting all your data if one save fails
- Natural separation of time periods

---

## FAQ

**Q: Does this track passwords?**

A: No. But also YES. This program will monitor your keyboard input, which means that your passwords / login information will be recorded (one keystroke at a time). It is up to the user to decide what happens with the recorded data. If you are tracking activity and need to type a sensistive string, you can always STOP tracking temporarily. The program itself does not recognize words or phrases- only keystrokes.

**Q: Why must I use Python 3.11?**

A: Python 3.14 is too new and pynput hasn't been updated for it yet. Python 3.11 is the stable, tested version.

**Q: Why do I see a keyboard thread error?**

A: This is a known macOS/pynput compatibility issue. The error appears but keyboard tracking still works! You can safely ignore it.

**Q: Can I see my typing speed?**

A: Yes! Count the keystroke events per minute in the CSV files. Future versions may include an auto-analysis for typing speed and clicks-per-minute.

**Q: How do I stop tracking?**

A: Click the "STOP" button. Note: the listeners keep running in the background, but events won't be recorded.

**Q: Can I delete old data?**

A: Yes. Just delete CSV files from the `activity_data` folder.

**Q: Can I run this 24/7?**

A: Yes! It's designed to run continuously. Data auto-saves every minute.

**Q: Will this slow down my computer?**

A: No. It uses minimal resources and runs efficiently in the background.

---

## Credits

Code by Claude 
Prompts + edits by Traversable Dale 
(October 2025)

Built with:
- **Python 3.11** - Core language
- **Tkinter** - GUI framework
- **pynput** - Input monitoring
- **Pillow** - Image support (future features)

---

## License

Free to use for personal and educational purposes.

---

**Happy Tracking!**