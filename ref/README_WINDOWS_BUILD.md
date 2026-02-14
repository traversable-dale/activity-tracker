# Windows Build Guide - Activity Tracker

Quick reference for building Windows executables and installers.

---

## Prerequisites

Install these once:

```bash
# Install Python dependencies
pip install pynput pillow pywin32 psutil

# Install PyInstaller
pip install pyinstaller
```

**Download Inno Setup** (for installer): https://jrsoftware.org/isinfo.php

---

## Build Process

### Step 1: Convert Icon (One-Time Setup)

```bash
# Convert macOS .icns to Windows .ico
python -c "from PIL import Image; img = Image.open('ref/TDT-logo-white-circle.icns'); img.save('ref/TDT-logo-white-circle.ico', format='ICO', sizes=[(256, 256)])"
```

### Step 2: Build Executable

```bash
# Clean previous builds
rm -rf build/ dist/

# Build using spec file (RECOMMENDED)
python -m PyInstaller ActivityTracker.spec

# Output: dist/Activity Tracker/ folder with exe and dependencies
```

**Alternative - Manual build:**
```bash
python -m PyInstaller --windowed --name "Activity Tracker" --icon=ref/TDT-logo-white-circle.ico activity_tracker.py
```

### Step 3: Test the Executable

```bash
# Run from dist folder
"dist/Activity Tracker/Activity Tracker.exe"
```

Check:
- ✅ Window opens with custom icon
- ✅ Background image loads
- ✅ Tracking works (click around, type something)
- ✅ PAUSE/SUMMARY/FOLDER buttons work
- ✅ Data saves to `activity_data/` folder

### Step 4: Create Installer (Optional but Recommended)

1. **Open Inno Setup Compiler**
2. **File → Open** → Select `installer-setup.iss`
3. **Build → Compile** (or press F9)
4. **Done!** Installer is in `Output/Activity_Tracker_Setup_v0.2.0.exe`

---

## What Gets Created

### Folder Build Output
```
dist/
└── Activity Tracker/
    ├── Activity Tracker.exe          ← Main executable
    ├── python313.dll
    ├── _internal/                    ← Dependencies
    │   ├── PIL/
    │   ├── pynput/
    │   └── ... (many files)
    └── assets/
        └── bg/
            └── background.png
```

### Installer Output
```
Output/
└── Activity_Tracker_Setup_v0.2.0.exe    ← Distributable installer
```

---

## Installer Features

When users run `Activity_Tracker_Setup_v0.2.0.exe`:

1. **Welcome Screen** - Custom branded welcome message
2. **License Agreement** - (optional, currently disabled)
3. **Select Destination** - Choose install location (default: `C:\Program Files\Activity Tracker\`)
4. **Select Components** - Desktop shortcut option
5. **Ready to Install** - Confirm settings
6. **Installing** - Progress bar
7. **Finished** - Option to launch immediately

**What gets installed:**
- ✅ Application files to Program Files
- ✅ Start Menu shortcuts
- ✅ Desktop shortcut (if selected)
- ✅ Activity Data Folder shortcut
- ✅ Uninstaller

**On uninstall:**
- ✅ Removes application files
- ✅ Removes shortcuts
- ✅ Keeps user's activity data (by default)
- ✅ Deletes debug logs only

---

## Customizing the Installer

Edit `installer-setup.iss`:

### Change Welcome Message
```pascal
[CustomMessages]
english.WelcomeLabel2=Your custom welcome message here!
```

### Change Default Install Location
```pascal
[Setup]
DefaultDirName={autopf}\YourFolderName
```

### Delete User Data on Uninstall
Uncomment this line in `[UninstallDelete]`:
```pascal
Type: filesandordirs; Name: "{app}\activity_data"
```

### Add License Agreement
```pascal
[Setup]
LicenseFile=LICENSE.txt
```

---

## Troubleshooting

### "pyinstaller: command not found"
Run as Python module instead:
```bash
python -m PyInstaller ActivityTracker.spec
```

### Icon not found error
Make sure you converted the icon first:
```bash
python -c "from PIL import Image; img = Image.open('ref/TDT-logo-white-circle.icns'); img.save('ref/TDT-logo-white-circle.ico', format='ICO', sizes=[(256, 256)])"
```

### Background image not loading
Check that `assets/bg/background.png` exists. The spec file includes it automatically.

### Executable is slow to start
This is normal for PyInstaller folder builds (~1-2 seconds). If using single-file mode, it's slower (~5-10 seconds).

### "Missing VCRUNTIME140.dll" error
Install Microsoft Visual C++ Redistributable:
https://aka.ms/vs/17/release/vc_redist.x64.exe

### Antivirus flags the .exe
This is common with PyInstaller executables. Solutions:
- Use folder mode (less suspicious than single-file)
- Sign the executable with a code signing certificate
- Submit to antivirus vendors for whitelisting
- Document this in distribution notes

---

## Distribution Checklist

Before sharing the installer:

- [ ] Test on a clean Windows machine
- [ ] Verify all buttons work
- [ ] Check tracking captures events
- [ ] Test SUMMARY report generation
- [ ] Verify data saves to correct location
- [ ] Test uninstaller
- [ ] Check that activity data persists after uninstall
- [ ] Test desktop shortcut (if created)
- [ ] Test Start Menu shortcuts

---

## File Sizes

Approximate sizes:
- **Folder build**: ~50-60 MB
- **Installer**: ~35-40 MB (compressed)
- **Installed**: ~55-65 MB on disk

---

## Quick Commands Reference

```bash
# Build exe
python -m PyInstaller ActivityTracker.spec

# Test exe
"dist/Activity Tracker/Activity Tracker.exe"

# Clean builds
rm -rf build/ dist/

# Full rebuild
rm -rf build/ dist/ && python -m PyInstaller ActivityTracker.spec
```

---

## Notes

- **Spec files** save your build configuration
- **Folder mode** is faster and better for installers
- **Single-file mode** is easier to share but slower to start
- **Inno Setup** is industry-standard for Windows installers
- **Background image** and **icon** are bundled automatically via spec file
- **Data folder** gets created on first run with proper permissions

---

**Last Updated:** February 2026  
**For:** Activity Tracker v0.2.0
