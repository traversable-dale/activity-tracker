# Installer Customization Guide

Quick reference for customizing your Activity Tracker installer.

---

## Text Customization

### Welcome Message (Lines 76-78)

```pascal
english.WelcomeLabel2=This wizard will install Activity Tracker v{#MyAppVersion}...
```

**Change to your own message:**
```pascal
english.WelcomeLabel2=Your custom welcome text here!%n%nUse %n for line breaks.
```

### Finish Message (Lines 81-82)

```pascal
english.FinishLabel=Activity Tracker has been successfully installed!
```

**Make it more exciting:**
```pascal
english.FinishLabel=Installation complete! Start tracking your productivity now.
```

### Button Text (Lines 91-95)

```pascal
ButtonNext=&Next >
ButtonInstall=&Install
```

**Change button labels:**
```pascal
ButtonNext=Continue >
ButtonInstall=Let's Go!
```

---

## Image Customization

### Required Image Sizes

**1. Sidebar Image** (Left side of installer)
- **Size:** 164 × 314 pixels
- **Format:** 24-bit BMP
- **File:** `installer_images/wizard-sidebar.bmp`

**2. Small Icon** (Top-right corner)
- **Size:** 55 × 55 pixels  
- **Format:** 24-bit BMP
- **File:** `installer_images/wizard-small.bmp`

### How to Add Custom Images

1. **Create the images** using any graphics editor (Paint.NET, Photoshop, GIMP)
2. **Save as BMP** (24-bit format, not 32-bit)
3. **Create folder:** `installer_images/` in your project root
4. **Place files:**
   ```
   activity-tracker/
   ├── installer_images/
   │   ├── wizard-sidebar.bmp    (164x314)
   │   └── wizard-small.bmp      (55x55)
   └── installer-setup-enhanced.iss
   ```
5. **Uncomment lines 50-51** in the `.iss` file:
   ```pascal
   ; Before:
   ; WizardImageFile=installer_images\wizard-sidebar.bmp
   ; WizardSmallImageFile=installer_images\wizard-small.bmp
   
   ; After:
   WizardImageFile=installer_images\wizard-sidebar.bmp
   WizardSmallImageFile=installer_images\wizard-small.bmp
   ```
6. **Recompile** the installer

---

## Color Customization

Unfortunately, Inno Setup doesn't support custom colors easily. But you can:

### Use Images for Branding
- Create a branded sidebar image (164×314) with your colors
- This gives you full control over the left side appearance

### Modern vs Classic Style

**Current (Modern):**
```pascal
WizardStyle=modern
```

**Classic Windows style:**
```pascal
WizardStyle=classic
```

---

## Advanced Customizations

### Change App Name Display

**Line 14:**
```pascal
#define MyAppName "Activity Tracker"
```

**Change to:**
```pascal
#define MyAppName "Your Custom Name"
```

### Change Publisher Info

**Line 16:**
```pascal
#define MyAppPublisher "Traversable Dale"
```

### Change Install Location

**Line 35:**
```pascal
DefaultDirName={autopf}\{#MyAppName}
```

**Change to custom folder:**
```pascal
DefaultDirName=C:\MyApps\ActivityTracker
```

### Add License Agreement

Add this to the `[Setup]` section:
```pascal
LicenseFile=LICENSE.txt
InfoBeforeFile=README.txt
```

Then create `LICENSE.txt` with your license text.

### Custom Finish Page Text

**Lines 81-82:**
```pascal
english.FinishLabel=Activity Tracker has been successfully installed!%n%nYou can now start tracking...
```

Add more info:
```pascal
english.FinishLabel=✓ Installation complete!%n%n📊 Generate reports with SUMMARY button%n📁 View data with FOLDER button%n⏸️ Pause tracking anytime for privacy
```

---

## Quick Customization Checklist

**Before building installer:**

- [ ] Update welcome message (line 77)
- [ ] Update finish message (line 81)
- [ ] Change publisher name if desired (line 16)
- [ ] Update website URL (line 17)
- [ ] Create custom images (optional)
- [ ] Add license file (optional)
- [ ] Test on clean Windows machine

---

## Testing Your Changes

1. **Edit** `installer-setup-enhanced.iss`
2. **Save** the file
3. **Open** in Inno Setup Compiler
4. **Press F9** to compile
5. **Run** `Output/Activity_Tracker_Setup_v0.2.0.exe`
6. **Check** that your custom text/images appear

---

## Example: Simple Customization

Here's a quick example of custom text:

```pascal
[CustomMessages]
english.WelcomeLabel1=Welcome to Activity Tracker!
english.WelcomeLabel2=Thanks for downloading!%n%nThis tool helps you:%n• Track computer usage%n• Generate productivity reports%n• Understand your work patterns%n%nAll data stays private on your PC.%n%nClick Next to install.

english.FinishLabel=You're all set!%n%n✓ Activity Tracker is installed%n✓ Start tracking from the Start Menu%n✓ Check out the README for tips
```

---

## Image Creation Tips

### Sidebar Image (164×314)
- Use your brand colors
- Add your logo at the top
- Keep it simple and clean
- Test with light/dark Windows themes
- Export as 24-bit BMP (not PNG!)

### Small Icon (55×55)
- Use your app icon
- Make sure it's visible at small size
- Center the icon
- Export as 24-bit BMP

### Free Tools for Creating Images
- **Paint.NET** (Windows) - Free, easy
- **GIMP** - Free, powerful
- **Photoshop** - Professional
- **Canva** - Online, templates

---

## Common Issues

**Images don't show:**
- Check file paths are correct
- Verify images are 24-bit BMP (not 32-bit or PNG)
- Make sure files exist before compiling

**Text looks weird:**
- Use `%n` for line breaks, not `\n`
- Avoid special characters
- Test with different Windows font sizes

**Colors don't match:**
- Create branded sidebar image instead
- Windows controls button/background colors

---

**Happy customizing!** 🎨
