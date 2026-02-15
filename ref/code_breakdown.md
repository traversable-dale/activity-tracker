# Activity Tracker — Code Breakdown

Section-by-section review of the codebase, covering how it works, where it runs, and data security implications.

---

## `activity_tracker.py`

### 1. Logging Setup (~lines 15–60)

**What it does:** Creates a rotating log file at `activity_data/debug.log` next to the script. Caps at 2MB with 3 backups.

**Local?** Yes. Uses `os.path.dirname(os.path.abspath(__file__))` to resolve the script's own directory. No remote logging.

**Security note:** The debug log records app names, event counts, and sampled event details (every 50th keystroke, all clicks). It doesn't log raw keystrokes, but it does log which application was active. If someone gains access to the log, they can see your app usage patterns and timestamps. The log level is set to `DEBUG` by default — you could tighten this to `logging.INFO` in production.

---

### 2. Platform-Specific Imports (~lines 62–90)

**What it does:** Conditionally imports OS-specific libraries:
- **macOS:** `AppKit` and `Quartz` (for getting the active app name)
- **Windows:** `win32gui`, `win32process`, `psutil` (same purpose)
- **Both:** `pynput` for keyboard/mouse listening

**Local?** Yes. These are all local system APIs. No network calls.

**Security note:** On macOS, this requires Accessibility and Input Monitoring permissions — the OS explicitly asks the user to grant these. On Windows, no special permissions are needed, which means the app can silently monitor input without the user being prompted by the OS. This is worth flagging to end users.

---

### 3. Customization Settings (~lines 93–117)

**What it does:** Defines constants for window size, colors, fonts, and a background image path. All cosmetic.

**Security note:** None. These are visual-only settings.

---

### 4. `ActivityTracker` Class

#### 4a. Keystroke Categorization (~lines 123–130)

**What it does:** Defines two sets — `SEPARATOR_KEYS` (space, enter, tab) and `MODIFIER_KEYS` (shift, ctrl, arrows, function keys). Every keystroke is classified as `char`, `separator`, or `modifier` instead of storing the actual character typed.

**Security note:** This is the core privacy mechanism. Raw text is never stored. Someone reading the CSV would see `char, char, char, separator` — they'd know you typed a 3-letter word but not which one. This is a good design choice. However, combined with the app name and timestamp, an adversary with enough data could potentially infer patterns (e.g., "typed 5 chars in a password field at 9:02 AM").

#### 4b. `__init__` (~lines 132–165)

**What it does:** Sets up data folder, autosave interval (default 60s, GUI overrides to 30s), session tracking variables. Data folder is `activity_data/` next to the script.

**Local?** Yes. `os.path.dirname(os.path.abspath(__file__))` anchors everything to the script's location.

#### 4c. `get_active_application()` (~lines 167–190)

**What it does:** Queries the OS for the currently focused application name.
- macOS: `NSWorkspace.sharedWorkspace().activeApplication()` → returns something like "Google Chrome"
- Windows: Gets foreground window handle → looks up the process ID → returns the process name (e.g., `chrome.exe`)

**Security note:** This records which app you're using at every single event. Over time, this builds a detailed timeline of your application usage. The Windows path uses `psutil.Process(pid).name()` which returns the executable name, not the window title — so it won't capture what tab/document you have open. The macOS path returns the application display name, also not the window title.

#### 4d. `record_event()` (~lines 192–215)

**What it does:** Creates an event dict with timestamp (ISO format), app name, event type, and key category. Appends to an in-memory list. Triggers autosave if the interval has elapsed.

**Security note:** Events accumulate in memory (`self.session_events` list) until saved. If the app crashes before a save, unsaved events are lost (which is actually good for privacy — no partial data leaking). The autosave writes everything to disk at regular intervals.

#### 4e. `on_key_press()` (~lines 217–237)

**What it does:** The pynput callback. Extracts the key name, then categorizes it into `char`/`separator`/`modifier`. Passes only the category to `record_event()`.

**Security note:** The raw `key.char` value is read but immediately discarded after categorization. It never reaches the CSV. This is the critical privacy boundary.

#### 4f. `on_click()` (~lines 239–243)

**What it does:** Records mouse clicks with button name (`left`, `right`, `middle`). Only fires on press, not release.

**Security note:** No position data (x, y coordinates are received by the callback but not stored). This is a deliberate privacy choice.

#### 4g. `start_tracking()` / `stop_tracking()` / `pause_tracking()` / `resume_tracking()` (~lines 245–295)

**What it does:**
- `start_tracking()` creates a new session ID (timestamp-based), sets up a new CSV file path, and on first call, starts pynput listeners as daemon threads.
- `stop_tracking()` sets `self.tracking = False` and saves.
- `pause_tracking()` sets `self.paused = True` — listeners keep running but `record_event()` returns early.
- `resume_tracking()` flips `paused` back to False.

**Security note:** The pause feature is designed for typing passwords or sensitive input. However, the listeners remain active even when paused — pynput is still receiving every keystroke, the app just discards them in software. The OS-level input monitoring permission stays active. A compromised version of this app could easily remove the `if self.paused: return` check and capture everything.

#### 4h. `save_session()` (~lines 297–310)

**What it does:** Writes all events to a CSV file using `csv.DictWriter`. UTF-8 encoding. Overwrites the file each time (not append mode).

**Security note:** The file is overwritten on each save, meaning partial saves during a session contain all events up to that point. Files are plain-text CSV with no encryption. Anyone with file system access can read them.

#### 4i. `load_all_sessions()` / `get_session_count()` (~lines 312–340)

**What it does:** Globs for `session_*.csv` files and reads them back. Used by the summary/report features.

**Security note:** No access control on the data files. Any process or user with filesystem access can read them.

---

### 5. `ActivitySummary` Class

#### 5a. Period Detection (`detect_periods` / `detect_periods_raw`) (~lines 355–460)

**What it does:** Walks through events chronologically and groups them into work/break/session-end periods based on time gaps:
- < 5 min gap → continuous work
- 5–30 min → short break
- 30 min – 1 hr → stepped away
- > 1 hr → session ended

`detect_periods_raw` keeps everything (for timeline display). `detect_periods` filters out session-end gaps and validates breaks (requires 10+ events after a break to count it).

**Security note:** This is purely analytical — it infers behavior from timestamps. The "stepped away" detection effectively tells someone when you left your computer and came back. Combined with app data, this creates a fairly detailed behavioral profile.

#### 5b. `count_words()` (~lines 462–500)

**What it does:** Estimates word count by counting sequences of `char` keystrokes followed by a `separator`. Includes legacy support for old data that stored raw key names.

**Security note:** None beyond what's already in the data. This is derived analysis.

#### 5c. `filter_events_by_date()` (~lines 502–540)

**What it does:** Filters events for a target date. Includes a session-aware check so that if a session starts at 11 PM and runs past midnight, all events stay grouped under the start date.

#### 5d. `analyze_events()` (~lines 542–640)

**What it does:** The main analytics engine. Calculates: total events, mouse/keyboard split, WPM, clicks per minute, work time, break time, per-application time breakdown. The per-app time calculation uses a 30-second threshold — if two consecutive events in the same app are more than 30 seconds apart, the gap doesn't count as active time.

**Security note:** The per-application breakdown is the most revealing piece. It shows exactly how much time you spent in each app, with keystroke and click counts. This is the kind of data employers might want — worth being aware of who has access to these reports.

#### 5e. `generate_summary_report()` / `generate_timeline()` (~lines 650–780)

**What it does:** Produces a human-readable `.txt` report and a machine-readable `.csv` report. The text report includes a timeline showing when you were working, on break, or away. Saves to `activity_data/reports/`.

**Security note:** The reports are the highest-risk files since they aggregate everything into an easy-to-read format. The CSV report is designed for ingestion by other tools (TouchDesigner is mentioned). These files persist indefinitely — there's no automatic cleanup or retention policy.

#### 5f. `save_csv_report()` (~lines 780–880)

**What it does:** Writes a flat CSV with rows like `metric, category, value, unit`. Includes both "today" and "lifetime" stats, plus per-program breakdowns.

---

### 6. `ActivityTrackerGUI` Class

#### 6a. `__init__` and window setup (~lines 890–960)

**What it does:** Creates a 320×120 Tkinter window. Tries to load a background image from `assets/bg/background.png`, applies an RGBA overlay if found, otherwise uses a solid color. Starts tracking automatically on launch in a daemon thread.

**Security note:** Tracking starts immediately with no confirmation dialog. The user doesn't explicitly opt in — launching the app is the opt-in. This is worth documenting clearly.

#### 6b. `create_ui()` (~lines 962–1060)

**What it does:** Lays out three buttons (PAUSE, SUMMARY, FOLDER) and two labels (status, stats). Two code paths depending on whether a background image loaded.

#### 6c. `show_summary()` (~lines 1080–1100)

**What it does:** Calls `generate_summary_report()`, then opens the text file using the OS default handler (`open` on macOS, `start` on Windows, `xdg-open` on Linux).

**Security note:** `subprocess.run(['open', report_file])` — this launches an external process. The file path is constructed internally (not user-supplied), so injection risk is minimal.

#### 6d. `open_data_folder()` (~lines 1102–1115)

**What it does:** Opens the `activity_data/` folder in the OS file manager.

#### 6e. `update_status()` (~lines 1120–1145)

**What it does:** Updates the stats label every 1 second via `root.after(1000, ...)`. Shows elapsed time and event count.

#### 6f. `on_closing()` (~lines 1150–1158)

**What it does:** Saves the session and destroys the window on close.

**Security note:** If the process is force-killed (e.g., `kill -9`), `on_closing` won't run and the last batch of unsaved events is lost. Data from the last autosave interval is at risk.

---

## `setup.py` (macOS build)

**What it does:** Configures py2app to bundle the script as a macOS `.app`. Includes the background image, excludes heavy libraries (matplotlib, numpy, scipy), and sets Info.plist values including the bundle identifier (`com.traversable.activitytracker`) and a permission description string.

**Security note:** The `NSAppleEventsUsageDescription` string is what macOS shows the user when requesting permissions. This is the transparency mechanism — macOS won't let the app monitor input without explicit user approval.

---

## `ActivityTracker.spec` (Windows build)

**What it does:** Configures PyInstaller to build a Windows `.exe`. Folder mode (not single-file). Includes the background image and icon. Hidden imports for `pynput.keyboard._win32` and `pynput.mouse._win32` (PyInstaller can't auto-detect these). Console is disabled (`console=False`).

**Security note:** `console=False` means there's no visible terminal window. The app runs silently in the background with just the small GUI. On Windows, since no OS permission prompt is required, this means the app can monitor all input with only a small 320×120 window as evidence it's running. This is the kind of setup that could be misused as spyware if distributed maliciously — worth being upfront about in documentation.

---

## `installer-setup.iss` (Windows installer)

**What it does:** Inno Setup script that creates a professional Windows installer wizard. Key details:

- Installs to `Program Files\Activity Tracker` by default
- `PrivilegesRequired=lowest` — doesn't need admin rights
- Creates an `activity_data` directory with `users-full` permissions
- Optional desktop and Start Menu shortcuts
- Offers to launch immediately after install
- On uninstall: deletes debug logs but **preserves user activity data by default** (there's a commented-out line to delete everything)

**Security notes:**
- `PrivilegesRequired=lowest` means it can install without admin, reducing the attack surface.
- `Permissions: users-full` on the data directory means any user on the machine can read/write the activity data — not just the user who installed it.
- The uninstall preserving data is a good default for user agency, but users should know their activity history survives uninstallation unless they manually delete it.
- The `AppId` GUID is hardcoded, which is fine for a single-publisher app.

---

## Summary of Key Security Considerations

### What's done well
- Keystroke categorization (no raw text capture)
- Mouse coordinates discarded
- No window titles or URLs recorded
- Fully offline — zero network calls anywhere in the codebase
- macOS requires explicit OS-level permission grants
- Pause feature for sensitive input

### What to be aware of
- All data files are unencrypted plaintext CSV
- No authentication or access control on data files
- Windows requires no OS permission prompt for input monitoring
- App usage patterns + timestamps can be quite revealing even without raw text
- No data retention policy or automatic cleanup
- Tracking starts immediately on launch with no consent dialog
- The installer's `users-full` permission on the data folder means other users on the same machine could access it
- Debug log at `DEBUG` level records sampled event details including app names
