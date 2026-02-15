; ===============================================================================
; Activity Tracker - Professional Windows Installer
; Enhanced with custom pages, sidebar images, and consent checkbox
;
; Prerequisites:
; 1. Build exe: python -m PyInstaller ActivityTracker.spec
; 2. Download Inno Setup: https://jrsoftware.org/isinfo.php
; 3. Place images in installer_images/ folder (see specs at bottom)
; 4. Compile: Open this file in Inno Setup -> Press F9
;
; Output: Activity_Tracker_Setup_v0.2.0.exe in Output/ folder
; ===============================================================================

#define MyAppName "Activity Tracker"
#define MyAppVersion "0.2.0"
#define MyAppPublisher "Traversable Dale"
#define MyAppURL "https://github.com/yourusername/activity-tracker"
#define MyAppExeName "Activity Tracker.exe"
#define MyAppDescription "Track keyboard and mouse activity by application"

[Setup]
; ===== App Information =====
AppId={{A7B3C4D5-1234-5678-9ABC-DEF012345678}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
AppCopyright=Copyright (C) 2025 {#MyAppPublisher}
AppComments={#MyAppDescription}

; ===== Installation Directories =====
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
AllowNoIcons=yes

; ===== Output Configuration =====
OutputDir=Output
OutputBaseFilename=Activity_Tracker_Setup_v{#MyAppVersion}
Compression=lzma
SolidCompression=yes

; ===== Visual Appearance =====
SetupIconFile=ref\TDT-logo-white-circle.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
WizardStyle=modern
DisableWelcomePage=no

; ===== CUSTOM IMAGES =====
; We load sidebar images programmatically per-page in [Code] below.
; Set the default to welcome.bmp (shown on Welcome page).
WizardImageFile=installer_images\welcome.bmp
WizardSmallImageFile=installer_images\wizard-small.bmp

; ===== Window Size =====
WizardSizePercent=120,100
WizardResizable=yes

; ===== User Permissions =====
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; ===== Version Information =====
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} Setup
VersionInfoCopyright=Copyright (C) 2025
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[CustomMessages]
; ===== WELCOME PAGE =====
english.WelcomeLabel1=Welcome to Activity Tracker
english.WelcomeLabel2=Version {#MyAppVersion}%nBy {#MyAppPublisher}%nCopyright (C) 2025%n%nActivity Tracker helps you understand your computer usage patterns by monitoring keyboard and mouse activity.%n%n- Track time spent in each application%n- Generate detailed activity reports (TXT + CSV)%n- Measure typing speed (WPM) and click rates%n- Analyze work periods and break patterns%n%nAll data stays 100%% private on your computer.%nNo internet connection required.%n%nLicense: Free for personal and educational use.%n%nClick Next to continue.

; ===== FINISH PAGE =====
; (FinishLabel set directly in [Messages] below)

[Messages]
WelcomeLabel1=Welcome to Activity Tracker
WelcomeLabel2=Version 0.2.0%nBy Traversable Dale%nCopyright (C) 2025%n%nActivity Tracker helps you understand your computer usage patterns by monitoring keyboard and mouse activity.%n%n- Track time spent in each application%n- Generate detailed activity reports (TXT + CSV)%n- Measure typing speed (WPM) and click rates%n- Analyze work periods and break patterns%n%nAll data stays 100%% private on your computer.%nNo internet connection required.%n%nLicense: Free for personal and educational use.%n%nClick Next to continue.
FinishedLabel=Activity Tracker has been successfully installed!%n%nThe app will begin tracking automatically when launched. Use the PAUSE button anytime to temporarily stop recording.%n%nYour activity data is stored locally in the app's activity_data folder.

; ===== Button Text =====
ButtonNext=&Next >
ButtonBack=< &Back
ButtonInstall=&Install
ButtonFinish=&Finish
ButtonCancel=Cancel

; ===== Page Titles =====
WizardSelectDir=Choose Install Location
SelectDirDesc=Where should Activity Tracker be installed?
SelectDirLabel3=Setup will install Activity Tracker in the following folder.

WizardReady=Ready to Install
ReadyLabel1=Setup is now ready to install Activity Tracker on your computer.
ReadyLabel2a=Click Install to continue with the installation, or click Back to review or change any settings.

FinishedHeadingLabel=Completing Activity Tracker Setup
ClickFinish=Click Finish to exit Setup.

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked
Name: "quicklaunchicon"; Description: "Create a &Quick Launch shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Include the entire dist folder from PyInstaller build
Source: "dist\Activity Tracker\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Bundle sidebar images into installer (extracted to temp at runtime for per-page swapping)
Source: "installer_images\welcome.bmp"; DestDir: "{tmp}"; Flags: dontcopy
Source: "installer_images\middle.bmp"; DestDir: "{tmp}"; Flags: dontcopy
Source: "installer_images\final.bmp"; DestDir: "{tmp}"; Flags: dontcopy

[Dirs]
; Create activity_data folder with user write permissions
Name: "{app}\activity_data"; Permissions: users-full

[Icons]
; Start Menu
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Comment: "Track your computer activity"
Name: "{group}\Activity Data Folder"; Filename: "{app}\activity_data"; Comment: "View saved activity data"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"; Comment: "Uninstall {#MyAppName}"

; Desktop (optional)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; Comment: "Track your computer activity"

; Quick Launch (legacy)
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; Option to launch after installation
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName} now"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up logs on uninstall (keeps session data by default)
Type: files; Name: "{app}\activity_data\debug.log"
Type: files; Name: "{app}\activity_data\debug.log.*"

; OPTIONAL: Delete ALL data on uninstall (including user's activity records)
; Uncomment this line to delete everything:
; Type: filesandordirs; Name: "{app}\activity_data"

[Code]
// ===============================================================================
// CUSTOM PAGE: "How It Works" (info only, no checkbox)
// SIDEBAR IMAGES: Extracted to temp dir, swapped per-page
// ===============================================================================

var
  HowItWorksPage: TWizardPage;
  InfoLabel: TRichEditViewer;

// Load a BMP into the wizard sidebar (left panel)
procedure SetWizardImage(ImagePath: String);
begin
  if FileExists(ImagePath) then
  begin
    WizardForm.WizardBitmapImage.Bitmap.LoadFromFile(ImagePath);
    WizardForm.WizardBitmapImage2.Bitmap.LoadFromFile(ImagePath);
  end;
end;

// Create the custom "How It Works" page
procedure InitializeWizard();
begin
  // Extract sidebar images from installer to temp directory
  ExtractTemporaryFile('welcome.bmp');
  ExtractTemporaryFile('middle.bmp');
  ExtractTemporaryFile('final.bmp');

  HowItWorksPage := CreateCustomPage(
    wpWelcome,
    'How Activity Tracker Works',
    'Please review how the application monitors your activity.'
  );

  InfoLabel := TRichEditViewer.Create(WizardForm);
  InfoLabel.Parent := HowItWorksPage.Surface;
  InfoLabel.Left := 0;
  InfoLabel.Top := 0;
  InfoLabel.Width := HowItWorksPage.SurfaceWidth;
  InfoLabel.Height := HowItWorksPage.SurfaceHeight;
  InfoLabel.ScrollBars := ssVertical;
  InfoLabel.ReadOnly := True;
  InfoLabel.TabStop := False;
  InfoLabel.UseRichEdit := False;
  InfoLabel.Lines.Add('Activity Tracker monitors your keyboard and mouse input to measure');
  InfoLabel.Lines.Add('your productivity patterns. Here is what you should know:');
  InfoLabel.Lines.Add('');
  InfoLabel.Lines.Add('WHAT GETS RECORDED');
  InfoLabel.Lines.Add('  - Keystroke categories only (character, separator, or modifier)');
  InfoLabel.Lines.Add('  - Mouse clicks (which button was pressed)');
  InfoLabel.Lines.Add('  - Which application is active (e.g. Chrome, Word)');
  InfoLabel.Lines.Add('  - Timestamps of each event');
  InfoLabel.Lines.Add('');
  InfoLabel.Lines.Add('WHAT IS NEVER RECORDED');
  InfoLabel.Lines.Add('  - The actual text you type (no raw keystrokes)');
  InfoLabel.Lines.Add('  - Screenshots or screen content');
  InfoLabel.Lines.Add('  - Window titles or URLs');
  InfoLabel.Lines.Add('  - Mouse cursor position');
  InfoLabel.Lines.Add('');
  InfoLabel.Lines.Add('PRIVACY');
  InfoLabel.Lines.Add('  - All data is stored locally on your computer');
  InfoLabel.Lines.Add('  - The app makes zero network connections');
  InfoLabel.Lines.Add('  - You can pause tracking at any time');
  InfoLabel.Lines.Add('  - Data is saved as plain CSV files you can inspect or delete');
end;

// Swap sidebar image based on which page is active
procedure CurPageChanged(CurPageID: Integer);
var
  TmpDir: String;
begin
  TmpDir := ExpandConstant('{tmp}');

  if CurPageID = wpWelcome then
    SetWizardImage(TmpDir + '\welcome.bmp')
  else if CurPageID = HowItWorksPage.ID then
    SetWizardImage(TmpDir + '\middle.bmp')
  else if CurPageID = wpFinished then
    SetWizardImage(TmpDir + '\final.bmp')
  else
    SetWizardImage(TmpDir + '\middle.bmp');
end;

// Pre-installation checks
function InitializeSetup(): Boolean;
begin
  Result := True;
end;

// Post-installation tasks
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Add any post-install actions here
  end;
end;

// ===============================================================================
// INSTALLER PAGE FLOW
// ===============================================================================
//
// 1. Welcome         -> welcome.bmp sidebar  (version + license info)
// 2. How It Works    -> middle.bmp sidebar    (privacy/tracking info)
// 3. Select Location -> middle.bmp sidebar
// 4. Select Tasks    -> middle.bmp sidebar
// 5. Ready           -> middle.bmp sidebar
// 6. Installing      -> middle.bmp sidebar
// 7. Finish          -> final.bmp sidebar
//
// ===============================================================================
