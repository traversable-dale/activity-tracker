# Windows Guide

Build, install, and customize Activity Tracker for Windows.

---

## Prerequisites

```bash
pip install pynput pillow pywin32 psutil pyinstaller
```

Download [Inno Setup 6](https://jrsoftware.org/isinfo.php) for the installer compiler.

---

## Build Process

### 1. Convert Icon (one-time)

```bash
python -c "from PIL import Image; img = Image.open('ref/TDT-logo-white-circle.icns'); img.save('ref/TDT-logo-white-circle.ico', format='ICO', sizes=[(256, 256)])"
```

### 2. Build Executable

```bash
rm -rf build/ dist/
python -m PyInstaller ActivityTracker.spec
```

Output goes to `dist/Activity Tracker/`.

### 3. Test

```bash
"dist/Activity Tracker/Activity Tracker.exe"
```

Verify: window opens with custom icon, background loads, tracking works, PAUSE/SUMMARY/FOLDER buttons work, data saves to `activity_data/`.

### 4. Create Installer

1. Open `installer-setup-custom.iss` in Inno Setup Compiler
2. Press F9 to compile
3. Output: `Output/Activity_Tracker_Setup_v0.2.0.exe`

---

## What Gets Created

### Folder Build

```
dist/
└── Activity Tracker/
    ├── Activity Tracker.exe
    ├── _internal/
    └── assets/bg/background.png
```

### Installer

```
Output/
└── Activity_Tracker_Setup_v0.2.0.exe
```

---

## Installer Pages

1. **Welcome** — Version info, feature overview, license
2. **How It Works** — What gets recorded, what doesn't, privacy info
3. **Choose Install Location** — Default: `AppData\Local\Programs\Activity Tracker`
4. **Select Additional Tasks** — Desktop shortcut option
5. **Ready to Install** — Confirmation
6. **Installing** — Progress bar
7. **Finish** — Option to launch immediately

On uninstall: removes app files and shortcuts, keeps user activity data by default, deletes debug logs only.

---

## Installer Images

All images go in `installer_images/` and must be 24-bit RGB BMP (no alpha).

| File | Size | Used On |
|------|------|---------|
| `welcome.bmp` | 164×314 px | Welcome page sidebar |
| `middle.bmp` | 164×314 px | Inner pages sidebar |
| `final.bmp` | 164×314 px | Finish page sidebar |
| `wizard-small.bmp` | 55×58 px | Top-right banner, all inner pages |

Convert from PNG with Pillow:

```python
from PIL import Image
img = Image.open("source.png").convert("RGBA")
rgb = Image.new("RGB", img.size, (0, 0, 0))
rgb.paste(img, mask=img.split()[3])
rgb.save("output.bmp", "BMP")
```

Images are bundled into the installer at compile time and extracted to temp at runtime.

---

## Installer Customization

### Welcome Page Text

Set directly in `[Messages]` section of the `.iss` file:

```pascal
WelcomeLabel1=Welcome to Activity Tracker
WelcomeLabel2=Version 0.2.0%nBy Traversable Dale%nCopyright (C) 2025%n%n...
```

Use `%n` for line breaks, `%%` for a literal percent sign. Note: `{#MyAppVersion}` preprocessor variables don't resolve in `[Messages]`, so version and publisher are hardcoded. Update them when you bump the version.

### Finish Page Text

```pascal
FinishedLabel=Activity Tracker has been successfully installed!%n%n...
```

### How It Works Page Text

Edit the `InfoLabel.Lines.Add(...)` calls in the `InitializeWizard` procedure in the `[Code]` section:

```pascal
InfoLabel.Lines.Add('Your custom text here');
```

### Button Text

```pascal
ButtonNext=&Next >
ButtonInstall=&Install
ButtonFinish=&Finish
```

The `&` marks the keyboard shortcut letter.

### App Identity

```pascal
#define MyAppName "Activity Tracker"
#define MyAppVersion "0.2.0"
#define MyAppPublisher "Traversable Dale"
#define MyAppURL "https://github.com/yourusername/activity-tracker"
```

These propagate to the installer title bar, Start Menu entries, and Windows Programs list.

### Install Location

```pascal
DefaultDirName={autopf}\{#MyAppName}
```

`{autopf}` resolves to `Program Files` (all users) or `AppData\Local\Programs` (current user) depending on install mode.

### Adding a License Agreement

Add to `[Setup]`:

```pascal
LicenseFile=LICENSE.txt
```

Create `LICENSE.txt` in your project root. Inno Setup will add a license page with an "I accept" checkbox.

### Uninstall Behavior

Currently keeps user data on uninstall, only removes debug logs:

```pascal
[UninstallDelete]
Type: files; Name: "{app}\activity_data\debug.log"
Type: files; Name: "{app}\activity_data\debug.log.*"
```

To delete all data on uninstall, uncomment:

```pascal
Type: filesandordirs; Name: "{app}\activity_data"
```

### Style

```pascal
WizardStyle=modern
```

Change to `classic` for the traditional Windows installer look. `WizardSizePercent=120,100` makes the window 20% wider than default.

---

## File Sizes

- Folder build: ~50-60 MB
- Installer: ~35-40 MB (compressed)
- Installed: ~55-65 MB on disk

---

## Troubleshooting

**"pyinstaller: command not found"** — Run as `python -m PyInstaller ActivityTracker.spec`

**Icon not found** — Convert the icon first (step 1 above).

**Background image not loading** — Check that `assets/bg/background.png` exists. The spec file includes it automatically.

**Executable slow to start** — Normal for PyInstaller folder builds (~1-2 sec). Single-file mode is slower (~5-10 sec).

**"Missing VCRUNTIME140.dll"** — Install [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe).

**Antivirus flags the .exe** — Common with PyInstaller. Use folder mode (less suspicious), or sign the executable with a code signing certificate.

**Installer images not showing** — All BMP files must be 24-bit RGB, no alpha. Sidebar images must be exactly 164×314 px. Small banner must be exactly 55×58 px.

**`{cm:...}` showing as literal text** — Custom message references don't resolve on Welcome or Finish pages. Set text directly in `[Messages]` instead.

**`#13#10` preprocessor error** — Never start a line with `#` inside `[Code]`. Keep `#13#10` inline with the preceding string.

**`;` comment error in `[Code]`** — Pascal Script uses `//` for comments, not `;`. The `;` character is a statement terminator in Pascal.

---

## Quick Commands

```bash
# Full rebuild
rm -rf build/ dist/ && python -m PyInstaller ActivityTracker.spec

# Test
"dist/Activity Tracker/Activity Tracker.exe"
```

---

## Distribution Checklist

- [ ] Test on a clean Windows machine
- [ ] Verify all buttons work
- [ ] Check tracking captures events
- [ ] Test SUMMARY report generation
- [ ] Verify data saves to correct location
- [ ] Test uninstaller
- [ ] Check activity data persists after uninstall
- [ ] Test desktop shortcut

---

Last updated: February 2026 — Activity Tracker v0.2.0
