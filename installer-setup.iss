; ===============================================================================
; Inno Setup Script for Activity Tracker
; Creates a professional Windows installer with GUI wizard
;
; Prerequisites:
; 1. Build the exe first: python -m PyInstaller ActivityTracker.spec
; 2. Download Inno Setup: https://jrsoftware.org/isinfo.php
; 3. Open this file in Inno Setup Compiler
; 4. Click "Build" → "Compile" (or press F9)
;
; Output: Activity_Tracker_Setup.exe in Output/ folder
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
WizardSizePercent=100,100

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
english.WelcomeLabel1=Welcome to Activity Tracker Setup
english.WelcomeLabel2=This wizard will guide you through the installation of %n%n{#MyAppName} v{#MyAppVersion}%n%nActivity Tracker monitors your keyboard and mouse activity, helping you understand your computer usage patterns. All data stays private on your computer.%n%nClick Next to continue, or Cancel to exit Setup.

[Messages]
; Custom welcome message
WelcomeLabel1={cm:WelcomeLabel1}
WelcomeLabel2={cm:WelcomeLabel2}

; Custom button text
ButtonNext=&Next >
ButtonBack=< &Back
ButtonInstall=&Install
ButtonFinish=&Finish

; Custom finish message
ClickFinish=Click Finish to exit Setup.
FinishedHeadingLabel=Completing Activity Tracker Setup
FinishedLabel={#MyAppName} has been installed on your computer.%n%nThe application will save activity data to:%n{app}\activity_data\%n%nClick Finish to close Setup.
FinishedRestartLabel=Setup has finished installing {#MyAppName}. Would you like to launch it now?

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked
Name: "quicklaunchicon"; Description: "Create a &Quick Launch shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Include the entire dist folder from PyInstaller build
Source: "dist\Activity Tracker\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Note: Don't use "Flags: ignoreversion" on any shared system files

[Dirs]
; Create activity_data folder with user write permissions
Name: "{app}\activity_data"; Permissions: users-full

[Icons]
; Start Menu
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Comment: "Track keyboard and mouse activity"
Name: "{group}\Activity Data Folder"; Filename: "{app}\activity_data"; Comment: "View saved activity data"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"; Comment: "Uninstall {#MyAppName}"

; Desktop (optional)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; Comment: "Track keyboard and mouse activity"

; Quick Launch (optional, legacy)
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; Option to launch after installation
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up logs on uninstall (keeps session data by default)
Type: files; Name: "{app}\activity_data\debug.log"
Type: files; Name: "{app}\activity_data\debug.log.*"

; Uncomment to delete ALL data on uninstall (including user's activity records)
; Type: filesandordirs; Name: "{app}\activity_data"

[Code]
// Custom code can go here for advanced installation logic

function InitializeSetup(): Boolean;
begin
  Result := True;
  // You can add pre-installation checks here
  // For example, check Python installation, display custom messages, etc.
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Post-installation tasks
    // For example, create initial config files
  end;
end;
