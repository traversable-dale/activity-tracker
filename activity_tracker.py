"""
Cross-Platform Activity Tracker - Compact & Customizable
Tracks keyboard and mouse activity by application

Dependencies:
pip install pynput pillow
"""

APP_VERSION = "0.2.0"

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import threading
import csv
import os
import logging
from logging.handlers import RotatingFileHandler
from collections import defaultdict
import glob
import subprocess
import platform
from PIL import Image, ImageTk


# ============ DEBUG LOGGING SETUP ============
# Log file: activity_data/debug.log (auto-rotates at 2MB, keeps 3 backups)
# Set to logging.INFO for quieter logs

DEBUG_LOG_LEVEL = logging.DEBUG

def setup_logger():
    """Configure rotating file logger for debug output"""
    logger = logging.getLogger('activity_tracker')
    logger.setLevel(DEBUG_LOG_LEVEL)
    if logger.handlers:
        return logger
    
    # Use script directory for log location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(script_dir, 'activity_data')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_path = os.path.join(log_dir, 'debug.log')
    
    file_handler = RotatingFileHandler(
        log_path, maxBytes=2*1024*1024, backupCount=3, encoding='utf-8'
    )
    file_handler.setLevel(DEBUG_LOG_LEVEL)
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-7s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Log the resolved path so we can debug path issues
    logger.info(f"Debug log initialized at: {log_path}")
    
    return logger

log = setup_logger()

# =============================================

# Fix for pynput on newer macOS/Python versions
try:
    from AppKit import NSEvent
    from Quartz import (
        CGEventCreateKeyboardEvent,
        CGEventPost,
        CGEventGetIntegerValueField,
        kCGEventSourceStateHIDSystemState,
        kCGKeyboardEventKeycode,
        kCGHIDEventTap
    )
    
    # Import pynput after setting up the fix
    from pynput import keyboard, mouse
    PYNPUT_AVAILABLE = True
except ImportError as e:
    log.warning(f"Could not import pynput or required libraries: {e}")
    PYNPUT_AVAILABLE = False

# Platform-specific imports
if platform.system() == 'Darwin':  # macOS
    from AppKit import NSWorkspace
elif platform.system() == 'Windows':
    import win32gui
    import win32process
    import psutil


# ============ CUSTOMIZATION SETTINGS ============
# Edit these to customize the appearance

WINDOW_SIZE = "320x120"

# Background: Use color OR image (image takes priority if found)
BG_COLOR = "#FFFFFF"  # Background color (used when no image)
BG_IMAGE_PATH = "assets/bg/background.png"  # Optional background image

# Button colors
BUTTON_PAUSE_BG = "#9C2D2D"    # Pause button (red-ish)
BUTTON_RESUME_BG = "#2D9C64"   # Resume button (green-ish) 
BUTTON_FOLDER_BG = "#2D649C"  
BUTTON_TEXT_COLOR = "#123456"  # Button text color

# Text colors
STATUS_TRACKING_COLOR = "#FFFFFF"  # "TRACKING" text color
STATUS_PAUSED_COLOR = "#FFFFFF"    # "PAUSED" text color  
STATS_TEXT_COLOR = "#FFFFFF"       # Stats text color (time & events)

# Font settings
FONT_FAMILY = "Arial"
FONT_SIZE_STATUS = 10
FONT_SIZE_BUTTON = 9

# ================================================


class ActivityTracker:
    """Main class for tracking keyboard and mouse activity"""
    
    # Keystroke categories for privacy-safe logging
    SEPARATOR_KEYS = {'space', 'enter', 'tab', 'return'}
    MODIFIER_KEYS = {'shift', 'shift_r', 'ctrl', 'ctrl_r', 'alt', 'alt_r', 
                     'cmd', 'cmd_r', 'caps_lock', 'backspace', 'delete',
                     'up', 'down', 'left', 'right', 'esc', 'home', 'end',
                     'page_up', 'page_down', 'f1', 'f2', 'f3', 'f4', 'f5',
                     'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12'}
    
    def __init__(self, autosave_interval=60):
        self.tracking = False
        self.paused = False  # For temporary pause (e.g. typing passwords)
        
        # Use script directory, not current working directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_folder = os.path.join(script_dir, 'activity_data')
        
        self.autosave_interval = autosave_interval
        self.last_save_time = datetime.now()
        
        # Create data folder if it doesn't exist
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
        
        log.info(f"ActivityTracker initialized — data folder: {self.data_folder}")
        log.info(f"  Autosave interval: {autosave_interval}s")
        
        # Current session data
        self.session_id = None
        self.session_file = None
        self.session_events = []
        
        # CSV header
        self.csv_header = ['timestamp', 'app', 'event_type', 'key']
        
        # Listeners - will be created once and kept running
        self.keyboard_listener = None
        self.mouse_listener = None
        self.listeners_started = False
        
        # Event counter for GUI feedback
        self.event_count = 0
        self.session_start = None
    
    def get_active_application(self):
        """Get the currently active application name"""
        try:
            if platform.system() == 'Darwin':  # macOS
                workspace = NSWorkspace.sharedWorkspace()
                if workspace is None:
                    return "Unknown"
                active_app = workspace.activeApplication()
                if active_app and 'NSApplicationName' in active_app:
                    return active_app['NSApplicationName']
                return "Unknown"
            
            elif platform.system() == 'Windows':
                # Get active window handle
                window = win32gui.GetForegroundWindow()
                # Get process ID from window
                _, pid = win32process.GetWindowThreadProcessId(window)
                # Get process name
                process = psutil.Process(pid)
                return process.name()
            
            else:
                return "Unknown"
        except Exception as e:
            # Silently handle errors and return Unknown
            return "Unknown"
    
    def record_event(self, event_type, key=None):
        """Record an activity event with privacy-safe keystroke categories"""
        if not self.tracking or self.paused:
            return
        
        event = {
            'timestamp': datetime.now().isoformat(),
            'app': self.get_active_application(),
            'event_type': event_type,
            'key': key if key else event_type
        }
        self.session_events.append(event)
        self.event_count += 1
        
        # Log sampled events (every 50th + all clicks) to avoid noise
        if event_type == 'click' or self.event_count % 50 == 0:
            log.debug(f"Event #{self.event_count} [{event['app']}] {event_type}: {key if key else 'N/A'}")
        
        # Auto-save if interval has passed
        if (datetime.now() - self.last_save_time).total_seconds() >= self.autosave_interval:
            self.save_session()
            self.last_save_time = datetime.now()
            log.info(f"Auto-saved: {len(self.session_events)} events | File: {self.session_file}")
    
    def on_key_press(self, key):
        """Callback for keyboard events — categorizes keystrokes for privacy"""
        try:
            # Determine the raw key name
            if hasattr(key, 'char') and key.char is not None:
                key_name = key.char
            else:
                key_name = str(key).replace('Key.', '')
            
            # Categorize the keystroke instead of storing the raw value
            if key_name in self.SEPARATOR_KEYS:
                self.record_event('keystroke', 'separator')
            elif key_name in self.MODIFIER_KEYS:
                self.record_event('keystroke', 'modifier')
            else:
                self.record_event('keystroke', 'char')
        except Exception as e:
            pass
    
    def on_click(self, x, y, button, pressed):
        """Callback for mouse click events"""
        if pressed:  # Only record on press, not release
            button_str = str(button).replace('Button.', '')
            self.record_event('click', button_str)
    
    def start_tracking(self):
        """Start tracking (or restart with new session)"""
        self.event_count = 0
        self.session_start = datetime.now()
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.session_file = os.path.join(self.data_folder, f'session_{self.session_id}.csv')
        self.session_events = []
        self.tracking = True
        self.paused = False
        
        log.info(f"Tracking started -- Session ID: {self.session_id}")
        log.info(f"  Session file: {self.session_file}")
        
        # Only create listeners once on first start
        if not self.listeners_started and PYNPUT_AVAILABLE:
            log.info("Creating input listeners for the first time...")
            
            try:
                self.keyboard_listener = keyboard.Listener(
                    on_press=self.on_key_press,
                    suppress=False
                )
                keyboard_thread = threading.Thread(target=self.keyboard_listener.start, daemon=True)
                keyboard_thread.start()
                
                import time
                time.sleep(0.3)
                log.info("Keyboard listener started successfully")
            except Exception as e:
                log.error(f"Keyboard listener error (may still work): {e}", exc_info=True)
            
            try:
                self.mouse_listener = mouse.Listener(on_click=self.on_click)
                self.mouse_listener.start()
                log.info("Mouse listener started successfully")
            except Exception as e:
                log.error(f"Error starting mouse listener: {e}", exc_info=True)
            
            self.listeners_started = True
        else:
            log.debug("Listeners already running, starting new session")
    
    def stop_tracking(self):
        """Stop tracking (but keep listeners running)"""
        self.tracking = False
        self.save_session()
        log.info(f"Tracking stopped. Saved {len(self.session_events)} events")
    
    def pause_tracking(self):
        """Temporarily pause recording (listeners stay active)"""
        self.paused = True
        log.info("Tracking paused")
    
    def resume_tracking(self):
        """Resume recording after pause"""
        self.paused = False
        log.info("Tracking resumed")
    
    def save_session(self):
        """Save current session to CSV file"""
        if not self.session_events:
            return
        
        try:
            # Write CSV file with UTF-8 encoding
            with open(self.session_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.csv_header)
                writer.writeheader()
                writer.writerows(self.session_events)
        except Exception as e:
            log.error(f"Error saving session: {e}", exc_info=True)
    
    def load_all_sessions(self):
        """Load all session files and return combined events"""
        all_events = []
        
        try:
            # Only load CSV files (ignore old JSON files)
            session_files = glob.glob(os.path.join(self.data_folder, 'session_*.csv'))
            
            for session_file in session_files:
                try:
                    with open(session_file, 'r', newline='', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            all_events.append(row)
                except Exception as e:
                    log.warning(f"Could not load session file {session_file}: {e}")
                    continue
        except Exception as e:
            log.error(f"Error loading sessions: {e}", exc_info=True)
        
        return all_events
    
    def get_session_count(self):
        """Get total number of session files"""
        try:
            session_files = glob.glob(os.path.join(self.data_folder, 'session_*.csv'))
            return len(session_files)
        except Exception as e:
            log.error(f"Error counting sessions: {e}")
            return 0


class ActivitySummary:
    """Analyze and summarize activity tracking data"""
    
    def __init__(self, data_folder='activity_data'):
        self.data_folder = data_folder
        self.break_threshold = 300  # 5 minutes in seconds
        self.session_timeout = 3600  # 1 hour — gaps longer than this = session ended
    
    def load_all_events(self):
        """Load all events from CSV files"""
        all_events = []
        session_files = glob.glob(os.path.join(self.data_folder, 'session_*.csv'))
        
        for session_file in session_files:
            try:
                with open(session_file, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        all_events.append(row)
            except Exception as e:
                log.warning(f"Could not load session file {session_file}: {e}")
        
        return all_events
    
    def parse_timestamp(self, timestamp_str):
        """Parse ISO timestamp string to datetime"""
        try:
            return datetime.fromisoformat(timestamp_str)
        except:
            return None
    
    def detect_periods_raw(self, events):
        """Detect working periods and breaks WITHOUT filtering - for timeline display.
        Gaps > session_timeout are marked as 'session_end'."""
        if not events:
            return []
        
        periods = []
        current_period = {
            'start': None, 'end': None, 'events': [], 'type': 'work'
        }
        
        for i, event in enumerate(events):
            timestamp = self.parse_timestamp(event['timestamp'])
            if not timestamp:
                continue
            
            if current_period['start'] is None:
                current_period['start'] = timestamp
                current_period['events'].append(event)
            else:
                last_timestamp = self.parse_timestamp(current_period['events'][-1]['timestamp'])
                time_gap = (timestamp - last_timestamp).total_seconds()
                
                if time_gap > self.session_timeout:
                    current_period['end'] = last_timestamp
                    periods.append(current_period)
                    periods.append({
                        'start': last_timestamp, 'end': timestamp,
                        'events': [], 'type': 'session_end'
                    })
                    current_period = {
                        'start': timestamp, 'end': None,
                        'events': [event], 'type': 'work'
                    }
                elif time_gap > self.break_threshold:
                    current_period['end'] = last_timestamp
                    periods.append(current_period)
                    periods.append({
                        'start': last_timestamp, 'end': timestamp,
                        'events': [], 'type': 'break'
                    })
                    current_period = {
                        'start': timestamp, 'end': None,
                        'events': [event], 'type': 'work'
                    }
                else:
                    current_period['events'].append(event)
        
        if current_period['events']:
            current_period['end'] = self.parse_timestamp(current_period['events'][-1]['timestamp'])
            periods.append(current_period)
        
        return periods
    
    def detect_periods(self, events):
        """Detect working periods, breaks, and session boundaries.
        
        Gap classification:
          < 5 min:           continuous work
          5-30 min:          short break
          30 min - 1 hr:     stepped away
          > 1 hr:            session ended (excluded from stats)
        """
        if not events:
            return []
        
        periods = []
        current_period = {
            'start': None, 'end': None, 'events': [], 'type': 'work'
        }
        
        for i, event in enumerate(events):
            timestamp = self.parse_timestamp(event['timestamp'])
            if not timestamp:
                continue
            
            if current_period['start'] is None:
                current_period['start'] = timestamp
                current_period['events'].append(event)
            else:
                last_timestamp = self.parse_timestamp(current_period['events'][-1]['timestamp'])
                time_gap = (timestamp - last_timestamp).total_seconds()
                
                if time_gap > self.session_timeout:
                    # SESSION ENDED — exclude from stats
                    current_period['end'] = last_timestamp
                    periods.append(current_period)
                    periods.append({
                        'start': last_timestamp, 'end': timestamp,
                        'events': [], 'type': 'session_end'
                    })
                    current_period = {
                        'start': timestamp, 'end': None,
                        'events': [event], 'type': 'work'
                    }
                elif time_gap > self.break_threshold:
                    # BREAK or STEPPED AWAY
                    current_period['end'] = last_timestamp
                    periods.append(current_period)
                    periods.append({
                        'start': last_timestamp, 'end': timestamp,
                        'events': [], 'type': 'break'
                    })
                    current_period = {
                        'start': timestamp, 'end': None,
                        'events': [event], 'type': 'work'
                    }
                else:
                    current_period['events'].append(event)
        
        if current_period['events']:
            current_period['end'] = self.parse_timestamp(current_period['events'][-1]['timestamp'])
            periods.append(current_period)
        
        # Filter: drop session_end markers, validate breaks
        filtered_periods = []
        for i, period in enumerate(periods):
            if period['type'] == 'session_end':
                continue
            elif period['type'] == 'break':
                has_work_after = False
                if i + 1 < len(periods):
                    next_period = periods[i + 1]
                    if next_period['type'] == 'work' and len(next_period['events']) >= 10:
                        has_work_after = True
                if has_work_after:
                    filtered_periods.append(period)
            else:
                filtered_periods.append(period)
        
        return filtered_periods
    
    def count_words(self, events):
        """Count words using keystroke categories (char/separator/modifier).
        A word = sequence of 'char' keystrokes followed by a 'separator'."""
        word_count = 0
        has_chars = False
        
        for event in events:
            if event['event_type'] == 'keystroke':
                key = event['key']
                if key == 'separator':
                    if has_chars:
                        word_count += 1
                        has_chars = False
                elif key == 'char':
                    has_chars = True
                # 'modifier' keys are ignored for word counting
                
                # Legacy support: handle old data with raw key values
                elif key in ('space', 'enter', 'tab', 'return', '.', 'period'):
                    if has_chars:
                        word_count += 1
                        has_chars = False
                elif key not in ('shift', 'ctrl', 'alt', 'cmd', 'shift_r',
                                'ctrl_r', 'alt_r', 'backspace', 'delete',
                                'up', 'down', 'left', 'right', 'esc',
                                'modifier'):
                    has_chars = True
        
        # Count final word if exists
        if has_chars:
            word_count += 1
        
        return word_count
    
    def filter_events_by_date(self, events, target_date):
        """Filter events that occurred on a specific date OR are part of a session that started on that date"""
        filtered = []
        session_starts = {}  # Track which session started on which date
        
        # Group events by session (consecutive events are same session)
        # A session is identified by gaps < break_threshold
        current_session_start = None
        
        for i, event in enumerate(events):
            timestamp = self.parse_timestamp(event['timestamp'])
            if not timestamp:
                continue
            
            # Check if this starts a new session (gap exceeds session timeout)
            if i > 0:
                prev_timestamp = self.parse_timestamp(events[i-1]['timestamp'])
                if prev_timestamp:
                    gap = (timestamp - prev_timestamp).total_seconds()
                    if gap > self.session_timeout:
                        # New session starting
                        current_session_start = timestamp.date()
            
            # First event starts first session
            if current_session_start is None:
                current_session_start = timestamp.date()
            
            # Include event if:
            # 1. Event date matches target, OR
            # 2. Session started on target date (even if event is next day)
            if timestamp.date() == target_date or current_session_start == target_date:
                filtered.append(event)
        
        return filtered
    
    def analyze_events(self, events, label="Summary"):
        """Analyze events and return statistics"""
        if not events:
            return None
        
        # Detect periods
        periods = self.detect_periods(events)
        work_periods = [p for p in periods if p['type'] == 'work']
        all_break_periods = [p for p in periods if p['type'] == 'break']
        
        # Separate short breaks (<30 min) from stepped away (>=30 min)
        short_breaks = []
        stepped_away = []
        for p in all_break_periods:
            if p['end']:
                duration_minutes = (p['end'] - p['start']).total_seconds() / 60
                if duration_minutes < 30:
                    short_breaks.append(p)
                else:
                    stepped_away.append(p)
        
        # Count events by type
        mouse_events = [e for e in events if e['event_type'] == 'click']
        keyboard_events = [e for e in events if e['event_type'] == 'keystroke']
        
        # Calculate first/last event timestamps (for display only)
        first_event = self.parse_timestamp(events[0]['timestamp'])
        last_event = self.parse_timestamp(events[-1]['timestamp'])
        
        # Calculate working time
        work_time = sum([(p['end'] - p['start']).total_seconds() 
                        for p in work_periods if p['end']])
        
        # Calculate break time (only short breaks, not stepped away)
        break_time = sum([(p['end'] - p['start']).total_seconds() 
                         for p in short_breaks if p['end']])
        
        # Calculate stepped away time
        stepped_away_time = sum([(p['end'] - p['start']).total_seconds() 
                                 for p in stepped_away if p['end']])
        
        # Total duration = work + breaks + stepped away (excludes session_end gaps)
        total_duration = work_time + break_time + stepped_away_time
        
        # Calculate averages
        avg_period_length = work_time / len(work_periods) if work_periods else 0
        avg_period_events = sum([len(p['events']) for p in work_periods]) / len(work_periods) if work_periods else 0
        avg_break_length = break_time / len(short_breaks) if short_breaks else 0
        avg_stepped_away_length = stepped_away_time / len(stepped_away) if stepped_away else 0
        
        # Count words and calculate WPM
        word_count = self.count_words(events)
        wpm = (word_count / (work_time / 60)) if work_time > 0 else 0
        
        # Calculate clicks per minute
        cpm = (len(mouse_events) / (work_time / 60)) if work_time > 0 else 0
        
        # Group by program - calculate ACTIVE time only
        program_stats = defaultdict(lambda: {'clicks': 0, 'keystrokes': 0, 'total': 0, 'time_seconds': 0})
        
        # Track active time per program (only count time between nearby events)
        activity_threshold = 30  # Count time between events if they're within 30 seconds
        
        for period in work_periods:
            if not period['events']:
                continue
            
            # Group events in this period by program
            period_programs = defaultdict(list)
            for event in period['events']:
                period_programs[event['app']].append(event)
            
            # Calculate ACTIVE time spent in each program
            for program, prog_events in period_programs.items():
                if len(prog_events) < 2:
                    # Single event - count as 1 second of activity
                    program_stats[program]['time_seconds'] += 1
                else:
                    # Sum up time between consecutive events if they're close together
                    for i in range(len(prog_events) - 1):
                        current_time = self.parse_timestamp(prog_events[i]['timestamp'])
                        next_time = self.parse_timestamp(prog_events[i + 1]['timestamp'])
                        gap = (next_time - current_time).total_seconds()
                        
                        # Only count the gap if events are close together (active usage)
                        if gap <= activity_threshold:
                            program_stats[program]['time_seconds'] += gap
                        # If gap > threshold, don't count that idle time
        
        # Count events per program
        for event in events:
            program = event['app']
            program_stats[program]['total'] += 1
            if event['event_type'] == 'click':
                program_stats[program]['clicks'] += 1
            elif event['event_type'] == 'keystroke':
                program_stats[program]['keystrokes'] += 1
        
        return {
            'label': label,
            'total_events': len(events),
            'mouse_events': len(mouse_events),
            'keyboard_events': len(keyboard_events),
            'word_count': word_count,
            'wpm': wpm,
            'cpm': cpm,
            'work_time_seconds': work_time,
            'work_periods': len(work_periods),
            'avg_period_length': avg_period_length,
            'avg_period_events': avg_period_events,
            'break_time_seconds': break_time,
            'num_breaks': len(short_breaks),
            'avg_break_length': avg_break_length,
            'stepped_away_time_seconds': stepped_away_time,
            'num_stepped_away': len(stepped_away),
            'avg_stepped_away_length': avg_stepped_away_length,
            'program_stats': dict(program_stats),
            'first_event': first_event,
            'last_event': last_event,
            'total_duration_seconds': total_duration
        }
    
    def format_time(self, seconds):
        """Format seconds into readable time string"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
    
    def generate_summary_report(self):
        """Generate comprehensive summary report and save to file"""
        # Create reports folder in data directory
        reports_folder = os.path.join(self.data_folder, 'reports')
        if not os.path.exists(reports_folder):
            os.makedirs(reports_folder)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = os.path.join(reports_folder, f'summary_{timestamp}.txt')
        csv_file = os.path.join(reports_folder, f'summary_{timestamp}.csv')
        
        # Build report content
        lines = []
        lines.append("=" * 60)
        lines.append("ACTIVITY TRACKER SUMMARY")
        lines.append("=" * 60)
        
        # Load all events
        all_events = self.load_all_events()
        if not all_events:
            lines.append("\nNo data found!")
            # Save and return
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            return report_file, None
        
        # Sort by timestamp
        all_events.sort(key=lambda x: x['timestamp'])
        
        # Get today's events
        today = datetime.now().date()
        today_events = self.filter_events_by_date(all_events, today)
        
        # Analyze today
        today_stats = None
        today_periods = []
        if today_events:
            lines.append("\n📅 TODAY'S SUMMARY")
            lines.append("-" * 60)
            today_stats = self.analyze_events(today_events, "Today")
            lines.extend(self.format_stats(today_stats))
            
            # Generate timeline - use RAW periods before filtering
            # This shows all gaps including ones at end of sessions
            raw_periods = self.detect_periods_raw(today_events)
            lines.extend(self.generate_timeline(raw_periods, "Today"))
            
            # Today's program table
            lines.append("\n📋 TODAY - PROGRAM USAGE TABLE")
            lines.append("-" * 60)
            lines.extend(self.format_program_table(today_stats['program_stats']))
        else:
            lines.append("\n📅 TODAY'S SUMMARY")
            lines.append("-" * 60)
            lines.append("No activity recorded today.")
        
        # Analyze lifetime
        lines.append("\n\n" + "=" * 60)
        lines.append("📊 LIFETIME SUMMARY")
        lines.append("=" * 60)
        lifetime_stats = self.analyze_events(all_events, "Lifetime")
        lines.extend(self.format_stats(lifetime_stats))
        
        # Lifetime program table
        lines.append("\n📋 LIFETIME - PROGRAM USAGE TABLE")
        lines.append("-" * 60)
        lines.extend(self.format_program_table(lifetime_stats['program_stats']))
        
        lines.append("\n" + "=" * 60)
        lines.append(f"Report generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 60)
        
        # Save text report
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        # Save CSV report
        self.save_csv_report(csv_file, today_stats, lifetime_stats)
        
        return report_file, csv_file
    
    def generate_timeline(self, periods, date_label="Today"):
        """Generate hourly timeline of work vs break periods"""
        if not periods:
            return []
        
        lines = []
        lines.append(f"\n🕐 {date_label.upper()} - HOURLY TIMELINE")
        lines.append("-" * 60)
        
        all_times = []
        for period in periods:
            if period['start']:
                all_times.append(period['start'])
            if period['end']:
                all_times.append(period['end'])
        
        if not all_times:
            lines.append("No activity data")
            return lines
        
        session_start = min(all_times)
        lines.append(f"{session_start.strftime('%I:%M %p').lstrip('0'):<15} | Session Started")
        
        for i, period in enumerate(periods):
            if not period['start'] or not period['end']:
                continue
            
            start_time = period['start'].strftime('%I:%M %p').lstrip('0')
            end_time = period['end'].strftime('%I:%M %p').lstrip('0')
            duration = (period['end'] - period['start']).total_seconds() / 60
            
            if period['type'] == 'session_end':
                lines.append(f"{start_time:<15} | Session Ended")
                lines.append(f"{'':15} |")
                lines.append(f"{end_time:<15} | Session Started")
            elif period['type'] == 'work':
                lines.append(f"{start_time:<15} | Working ({int(duration)} min)")
            elif period['type'] == 'break':
                if duration >= 30:
                    lines.append(f"{start_time:<15} | Stepped Away ({int(duration)} min)")
                else:
                    lines.append(f"{start_time:<15} | Break ({int(duration)} min)")
        
        session_end = max(all_times)
        lines.append(f"{session_end.strftime('%I:%M %p').lstrip('0'):<15} | Session Ended")
        
        return lines
    
    def save_csv_report(self, csv_file, today_stats, lifetime_stats):
        """Save summary metrics to CSV file for TouchDesigner"""
        rows = []
        
        # CSV Header
        rows.append(['metric', 'category', 'value', 'unit'])
        
        # Helper to add rows
        def add_metric(metric_name, category, value, unit=''):
            rows.append([metric_name, category, value, unit])
        
        # Today's metrics
        if today_stats:
            add_metric('session_duration_seconds', 'today', round(today_stats['total_duration_seconds'], 2), 'seconds')
            add_metric('session_duration_minutes', 'today', round(today_stats['total_duration_seconds'] / 60, 2), 'minutes')
            add_metric('session_duration_hours', 'today', round(today_stats['total_duration_seconds'] / 3600, 2), 'hours')
            add_metric('total_events', 'today', today_stats['total_events'], 'count')
            add_metric('mouse_events', 'today', today_stats['mouse_events'], 'count')
            add_metric('keyboard_events', 'today', today_stats['keyboard_events'], 'count')
            add_metric('word_count', 'today', today_stats['word_count'], 'count')
            add_metric('wpm', 'today', round(today_stats['wpm'], 2), 'words/min')
            add_metric('cpm', 'today', round(today_stats['cpm'], 2), 'clicks/min')
            add_metric('work_time_seconds', 'today', round(today_stats['work_time_seconds'], 2), 'seconds')
            add_metric('work_time_minutes', 'today', round(today_stats['work_time_seconds'] / 60, 2), 'minutes')
            add_metric('work_time_hours', 'today', round(today_stats['work_time_seconds'] / 3600, 2), 'hours')
            add_metric('work_periods', 'today', today_stats['work_periods'], 'count')
            add_metric('avg_period_length_seconds', 'today', round(today_stats['avg_period_length'], 2), 'seconds')
            add_metric('avg_period_length_minutes', 'today', round(today_stats['avg_period_length'] / 60, 2), 'minutes')
            add_metric('avg_period_events', 'today', round(today_stats['avg_period_events'], 2), 'count')
            add_metric('break_time_seconds', 'today', round(today_stats['break_time_seconds'], 2), 'seconds')
            add_metric('break_time_minutes', 'today', round(today_stats['break_time_seconds'] / 60, 2), 'minutes')
            add_metric('num_breaks', 'today', today_stats['num_breaks'], 'count')
            add_metric('avg_break_length_seconds', 'today', round(today_stats['avg_break_length'], 2), 'seconds')
            add_metric('avg_break_length_minutes', 'today', round(today_stats['avg_break_length'] / 60, 2), 'minutes')
            add_metric('stepped_away_time_seconds', 'today', round(today_stats['stepped_away_time_seconds'], 2), 'seconds')
            add_metric('stepped_away_time_minutes', 'today', round(today_stats['stepped_away_time_seconds'] / 60, 2), 'minutes')
            add_metric('num_stepped_away', 'today', today_stats['num_stepped_away'], 'count')
            add_metric('avg_stepped_away_length_seconds', 'today', round(today_stats['avg_stepped_away_length'], 2), 'seconds')
            add_metric('avg_stepped_away_length_minutes', 'today', round(today_stats['avg_stepped_away_length'] / 60, 2), 'minutes')
            
            # Today's program stats
            for program, stats in today_stats['program_stats'].items():
                add_metric(f'program_{program}_time_seconds', 'today_programs', round(stats['time_seconds'], 2), 'seconds')
                add_metric(f'program_{program}_time_minutes', 'today_programs', round(stats['time_seconds'] / 60, 2), 'minutes')
                add_metric(f'program_{program}_clicks', 'today_programs', stats['clicks'], 'count')
                add_metric(f'program_{program}_keystrokes', 'today_programs', stats['keystrokes'], 'count')
                add_metric(f'program_{program}_total', 'today_programs', stats['total'], 'count')
        
        # Lifetime metrics
        add_metric('session_duration_seconds', 'lifetime', round(lifetime_stats['total_duration_seconds'], 2), 'seconds')
        add_metric('session_duration_minutes', 'lifetime', round(lifetime_stats['total_duration_seconds'] / 60, 2), 'minutes')
        add_metric('session_duration_hours', 'lifetime', round(lifetime_stats['total_duration_seconds'] / 3600, 2), 'hours')
        add_metric('total_events', 'lifetime', lifetime_stats['total_events'], 'count')
        add_metric('mouse_events', 'lifetime', lifetime_stats['mouse_events'], 'count')
        add_metric('keyboard_events', 'lifetime', lifetime_stats['keyboard_events'], 'count')
        add_metric('word_count', 'lifetime', lifetime_stats['word_count'], 'count')
        add_metric('wpm', 'lifetime', round(lifetime_stats['wpm'], 2), 'words/min')
        add_metric('cpm', 'lifetime', round(lifetime_stats['cpm'], 2), 'clicks/min')
        add_metric('work_time_seconds', 'lifetime', round(lifetime_stats['work_time_seconds'], 2), 'seconds')
        add_metric('work_time_minutes', 'lifetime', round(lifetime_stats['work_time_seconds'] / 60, 2), 'minutes')
        add_metric('work_time_hours', 'lifetime', round(lifetime_stats['work_time_seconds'] / 3600, 2), 'hours')
        add_metric('work_periods', 'lifetime', lifetime_stats['work_periods'], 'count')
        add_metric('avg_period_length_seconds', 'lifetime', round(lifetime_stats['avg_period_length'], 2), 'seconds')
        add_metric('avg_period_length_minutes', 'lifetime', round(lifetime_stats['avg_period_length'] / 60, 2), 'minutes')
        add_metric('avg_period_events', 'lifetime', round(lifetime_stats['avg_period_events'], 2), 'count')
        add_metric('break_time_seconds', 'lifetime', round(lifetime_stats['break_time_seconds'], 2), 'seconds')
        add_metric('break_time_minutes', 'lifetime', round(lifetime_stats['break_time_seconds'] / 60, 2), 'minutes')
        add_metric('num_breaks', 'lifetime', lifetime_stats['num_breaks'], 'count')
        add_metric('avg_break_length_seconds', 'lifetime', round(lifetime_stats['avg_break_length'], 2), 'seconds')
        add_metric('avg_break_length_minutes', 'lifetime', round(lifetime_stats['avg_break_length'] / 60, 2), 'minutes')
        add_metric('stepped_away_time_seconds', 'lifetime', round(lifetime_stats['stepped_away_time_seconds'], 2), 'seconds')
        add_metric('stepped_away_time_minutes', 'lifetime', round(lifetime_stats['stepped_away_time_seconds'] / 60, 2), 'minutes')
        add_metric('num_stepped_away', 'lifetime', lifetime_stats['num_stepped_away'], 'count')
        add_metric('avg_stepped_away_length_seconds', 'lifetime', round(lifetime_stats['avg_stepped_away_length'], 2), 'seconds')
        add_metric('avg_stepped_away_length_minutes', 'lifetime', round(lifetime_stats['avg_stepped_away_length'] / 60, 2), 'minutes')
        
        # Lifetime program stats
        for program, stats in lifetime_stats['program_stats'].items():
            add_metric(f'program_{program}_time_seconds', 'lifetime_programs', round(stats['time_seconds'], 2), 'seconds')
            add_metric(f'program_{program}_time_minutes', 'lifetime_programs', round(stats['time_seconds'] / 60, 2), 'minutes')
            add_metric(f'program_{program}_clicks', 'lifetime_programs', stats['clicks'], 'count')
            add_metric(f'program_{program}_keystrokes', 'lifetime_programs', stats['keystrokes'], 'count')
            add_metric(f'program_{program}_total', 'lifetime_programs', stats['total'], 'count')
        
        # Metadata
        add_metric('report_timestamp', 'metadata', datetime.now().isoformat(), 'datetime')
        add_metric('report_date', 'metadata', datetime.now().strftime('%Y-%m-%d'), 'date')
        add_metric('report_time', 'metadata', datetime.now().strftime('%H:%M:%S'), 'time')
        
        # Timeline data (if today stats exist)
        if today_stats:
            # Detect periods again to get timeline
            today_events_list = []
            # We don't have access to today_events here, so we'll skip timeline in CSV
            # Timeline is more useful in the text report anyway
            pass
        
        # Write CSV
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(rows)
    
    def format_stats(self, stats):
        """Format statistics as list of strings"""
        if not stats:
            return []
        
        lines = []
        
        # Session duration info at top
        lines.append(f"\n📅 Session Duration: {self.format_time(stats['total_duration_seconds'])}")
        lines.append(f"  └─ Started: {stats['first_event'].strftime('%I:%M %p').lstrip('0')}")
        lines.append(f"  └─ Ended: {stats['last_event'].strftime('%I:%M %p').lstrip('0')}")
        
        lines.append(f"\n📊 Total Events: {stats['total_events']:,}")
        lines.append(f"  └─ Mouse: {stats['mouse_events']:,}")
        lines.append(f"  └─ Keyboard: {stats['keyboard_events']:,}")
        lines.append(f"\n⚡ Words per Minute: {stats['wpm']:.1f}")
        lines.append(f"⚡ Clicks per Minute: {stats['cpm']:.1f}")
        
        lines.append(f"\n⏱️  Time Working: {self.format_time(stats['work_time_seconds'])}")
        lines.append(f"  └─ Working Periods: {stats['work_periods']}")
        lines.append(f"  └─ Avg Period Length: {self.format_time(stats['avg_period_length'])}")
        lines.append(f"  └─ Avg Period Events: {stats['avg_period_events']:.0f}")
        
        lines.append(f"\n☕ Time on Break: {self.format_time(stats['break_time_seconds'])}")
        lines.append(f"  └─ Number of Breaks: {stats['num_breaks']}")
        if stats['num_breaks'] > 0:
            lines.append(f"  └─ Avg Break Length: {self.format_time(stats['avg_break_length'])}")
        
        # Add stepped away section
        if stats['num_stepped_away'] > 0:
            lines.append(f"\n🚶 Time Stepped Away: {self.format_time(stats['stepped_away_time_seconds'])}")
            lines.append(f"  └─ Times Stepped Away: {stats['num_stepped_away']}")
            lines.append(f"  └─ Avg Duration: {self.format_time(stats['avg_stepped_away_length'])}")
        
        return lines
    
    def format_program_table(self, program_stats):
        """Format program comparison table as list of strings"""
        if not program_stats:
            return []
        
        lines = []
        
        # Sort by total events
        sorted_programs = sorted(program_stats.items(), 
                                key=lambda x: x[1]['total'], 
                                reverse=True)
        
        # Print header
        lines.append(f"\n{'Program':<30} {'Time':>10} {'Clicks':>10} {'Keys':>10} {'Total':>10}")
        lines.append("-" * 73)
        
        # Print rows
        for program, stats in sorted_programs:
            time_str = self.format_time(stats['time_seconds'])
            lines.append(f"{program:<30} {time_str:>10} {stats['clicks']:>10,} {stats['keystrokes']:>10,} {stats['total']:>10,}")
        
        # Print totals
        total_time = sum([s['time_seconds'] for s in program_stats.values()])
        total_clicks = sum([s['clicks'] for s in program_stats.values()])
        total_keystrokes = sum([s['keystrokes'] for s in program_stats.values()])
        total_events = sum([s['total'] for s in program_stats.values()])
        lines.append("-" * 73)
        lines.append(f"{'TOTAL':<30} {self.format_time(total_time):>10} {total_clicks:>10,} {total_keystrokes:>10,} {total_events:>10,}")
        
        return lines


class ActivityTrackerGUI:
    """Compact customizable GUI for the Activity Tracker"""
    
    def __init__(self):
        self.tracker = ActivityTracker(autosave_interval=30)
        self.summary = ActivitySummary(data_folder=self.tracker.data_folder)
        
        # Create main window
        self.root = tk.Tk()
        self.root.title(f"Activity Tracker v{APP_VERSION}")
        self.root.geometry(WINDOW_SIZE)
        self.root.resizable(False, False)
        
        # Try to load background image, otherwise use color
        self.bg_image = None
        if os.path.exists(BG_IMAGE_PATH):
            try:
                img = Image.open(BG_IMAGE_PATH)
                # Resize to window size
                width, height = map(int, WINDOW_SIZE.split('x'))
                img = img.resize((width, height), Image.Resampling.LANCZOS)
                
                # Create semi-transparent black overlay (40% opacity)
                overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))  # Black with 40% opacity
                
                # Convert base image to RGBA and blend
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                blended = Image.alpha_composite(img, overlay)
                
                self.bg_image = ImageTk.PhotoImage(blended)
                log.debug(f"Loaded background image with overlay: {BG_IMAGE_PATH}")
            except Exception as e:
                log.warning(f"Could not load background image: {e}")
                self.bg_image = None
        
        # Set background
        if self.bg_image:
            # Create canvas for image background (now includes overlay)
            width, height = map(int, WINDOW_SIZE.split('x'))
            self.canvas = tk.Canvas(self.root, width=width, height=height, highlightthickness=0)
            self.canvas.pack(fill=tk.BOTH, expand=True)
            self.canvas.create_image(0, 0, image=self.bg_image, anchor=tk.NW)
            
            # We'll place widgets directly on canvas
            self.has_bg_image = True
        else:
            # Use solid color background
            self.root.configure(bg=BG_COLOR)
            self.has_bg_image = False
            self.main_frame = tk.Frame(self.root, bg=BG_COLOR)
            self.main_frame.pack(expand=True, fill=tk.BOTH)
        
        # Create UI
        self.create_ui()
        
        # Start tracking automatically
        self.tracking_thread = threading.Thread(target=self.tracker.start_tracking, daemon=True)
        self.tracking_thread.start()
        
        # Delay status updates slightly to let UI stabilize
        self.root.after(500, self.update_status)
    
    def create_ui(self):
        """Create the compact user interface"""
        try:
            if self.has_bg_image:
                # Place elements directly on canvas with solid backgrounds
                width, height = map(int, WINDOW_SIZE.split('x'))
                
                # Status label at top
                self.status_label = tk.Label(self.root, text="TRACKING", 
                                             font=(FONT_FAMILY, FONT_SIZE_STATUS, 'bold'), 
                                             fg=STATUS_TRACKING_COLOR, bg='#000000')
                self.canvas.create_window(width//2, 20, window=self.status_label)
                
                # Create buttons — 3 buttons: PAUSE, SUMMARY, FOLDER
                button_y = height//2
                button_spacing = 80
                start_x = width//2 - button_spacing
                
                self.pause_btn = tk.Button(self.root, text="PAUSE",
                                           command=self.toggle_pause,
                                           font=(FONT_FAMILY, FONT_SIZE_BUTTON, 'bold'),
                                           bg=BUTTON_PAUSE_BG, fg=BUTTON_TEXT_COLOR,
                                           width=7, height=1, 
                                           relief=tk.FLAT, bd=0)
                self.canvas.create_window(start_x, button_y, window=self.pause_btn)
                
                self.summary_btn = tk.Button(self.root, text="SUMMARY",
                                            command=self.show_summary,
                                            font=(FONT_FAMILY, FONT_SIZE_BUTTON, 'bold'),
                                            bg="#2D9C9C", fg=BUTTON_TEXT_COLOR,
                                            width=7, height=1,
                                            relief=tk.FLAT, bd=0)
                self.canvas.create_window(start_x + button_spacing, button_y, window=self.summary_btn)
                
                self.folder_btn = tk.Button(self.root, text="FOLDER",
                                           command=self.open_data_folder,
                                           font=(FONT_FAMILY, FONT_SIZE_BUTTON, 'bold'),
                                           bg=BUTTON_FOLDER_BG, fg=BUTTON_TEXT_COLOR,
                                           width=7, height=1,
                                           relief=tk.FLAT, bd=0)
                self.canvas.create_window(start_x + button_spacing*2, button_y, window=self.folder_btn)
                
                # Stats label at bottom  
                self.stats_label = tk.Label(self.root, text="0m 0s | 0 events", 
                                            font=(FONT_FAMILY, 7), 
                                            fg=STATS_TEXT_COLOR, bg='#000000')
                self.canvas.create_window(width//2, height - 15, window=self.stats_label)
                
            else:
                # Use frame-based layout (no background image)
                self.status_label = tk.Label(self.main_frame, text="TRACKING", 
                                             font=(FONT_FAMILY, FONT_SIZE_STATUS, 'bold'), 
                                             bg=BG_COLOR, fg='#000000')
                self.status_label.pack(pady=5)
                
                button_frame = tk.Frame(self.main_frame, bg=BG_COLOR)
                button_frame.pack(pady=5)
                
                self.pause_btn = tk.Button(button_frame, text="PAUSE",
                                           command=self.toggle_pause,
                                           font=(FONT_FAMILY, FONT_SIZE_BUTTON, 'bold'),
                                           bg=BUTTON_PAUSE_BG, fg='#FFFFFF',
                                           width=7, height=1, 
                                           relief=tk.FLAT, bd=0)
                self.pause_btn.pack(side=tk.LEFT, padx=2)
                
                self.summary_btn = tk.Button(button_frame, text="SUMMARY",
                                            command=self.show_summary,
                                            font=(FONT_FAMILY, FONT_SIZE_BUTTON, 'bold'),
                                            bg="#2D9C9C", fg='#FFFFFF',
                                            width=7, height=1,
                                            relief=tk.FLAT, bd=0)
                self.summary_btn.pack(side=tk.LEFT, padx=2)
                
                self.folder_btn = tk.Button(button_frame, text="FOLDER",
                                           command=self.open_data_folder,
                                           font=(FONT_FAMILY, FONT_SIZE_BUTTON, 'bold'),
                                           bg=BUTTON_FOLDER_BG, fg='#FFFFFF',
                                           width=7, height=1,
                                           relief=tk.FLAT, bd=0)
                self.folder_btn.pack(side=tk.LEFT, padx=2)
                
                self.stats_label = tk.Label(self.main_frame, text="0m 0s | 0 events", 
                                            font=(FONT_FAMILY, 7), 
                                            bg=BG_COLOR, fg='#000000')
                self.stats_label.pack(pady=5)
            
        except Exception as e:
            log.error(f"Error creating UI: {e}", exc_info=True)
    
    def _darken_color(self, hex_color):
        """Darken a hex color by 20% for active state"""
        try:
            hex_color = hex_color.lstrip('#')
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            r, g, b = int(r * 0.8), int(g * 0.8), int(b * 0.8)
            return f'#{r:02x}{g:02x}{b:02x}'
        except:
            return hex_color
    
    def toggle_pause(self):
        """Toggle pause/resume for temporary privacy (e.g. typing passwords)"""
        try:
            if self.tracker.paused:
                self.tracker.resume_tracking()
                self.pause_btn.config(text="PAUSE", bg=BUTTON_PAUSE_BG, fg=BUTTON_TEXT_COLOR)
                self.status_label.config(text="TRACKING", fg=STATUS_TRACKING_COLOR)
            else:
                self.tracker.pause_tracking()
                self.pause_btn.config(text="RESUME", bg=BUTTON_RESUME_BG, fg=BUTTON_TEXT_COLOR)
                self.status_label.config(text="PAUSED", fg=STATUS_PAUSED_COLOR)
        except Exception as e:
            log.error(f"Error toggling pause: {e}", exc_info=True)
    
    def show_summary(self):
        """Generate and display activity summary in a file"""
        log.info("Generating summary report...")
        
        # Generate report (this returns the file paths)
        report_file, csv_file = self.summary.generate_summary_report()
        
        log.info(f"Text report saved to: {report_file}")
        if csv_file:
            log.info(f"CSV report saved to: {csv_file}")
        
        # Open the text file automatically
        try:
            if platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', report_file])
            elif platform.system() == 'Windows':
                subprocess.run(['start', report_file], shell=True)
            else:  # Linux
                subprocess.run(['xdg-open', report_file])
            log.info("Report opened successfully")
        except Exception as e:
            log.warning(f"Report saved but could not auto-open: {e}")
            log.info(f"Manual open path: {report_file}")
    
    def open_data_folder(self):
        """Open the activity_data folder"""
        folder_path = os.path.abspath(self.tracker.data_folder)
        
        try:
            if platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', folder_path])
            elif platform.system() == 'Windows':
                subprocess.run(['explorer', folder_path])
            else:  # Linux
                subprocess.run(['xdg-open', folder_path])
            log.debug(f"Opened folder: {folder_path}")
        except Exception as e:
            log.warning(f"Could not open folder: {e}")
    
    def start_status_updates(self):
        """Start the status update loop"""
        self.update_status()
    
    def update_status(self):
        """Update status display"""
        try:
            if self.tracker.tracking and self.tracker.session_start:
                session_duration = (datetime.now() - self.tracker.session_start).total_seconds()
                minutes = int(session_duration // 60)
                seconds = int(session_duration % 60)
                paused_indicator = " (PAUSED)" if self.tracker.paused else ""
                stats_text = f"{minutes}m {seconds}s | {self.tracker.event_count} events{paused_indicator}"
            else:
                stats_text = "Starting..."
            
            if hasattr(self, 'stats_label') and self.stats_label.winfo_exists():
                self.stats_label.config(text=stats_text)
        except Exception as e:
            log.debug(f"Status update error: {e}")
        
        # Schedule next update
        try:
            if self.root.winfo_exists():
                self.root.after(1000, self.update_status)
        except:
            pass
    
    def run(self):
        """Start the GUI"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Clean up when closing"""
        log.info("Application closing -- saving final session...")
        self.tracker.stop_tracking()
        log.info("Goodbye!")
        self.root.destroy()


if __name__ == "__main__":
    log.info("=" * 50)
    log.info(f"Activity Tracker v{APP_VERSION}")
    log.info(f"Platform: {platform.system()} | Python: {platform.python_version()}")
    log.info(f"pynput available: {PYNPUT_AVAILABLE}")
    log.info("=" * 50)
    app = ActivityTrackerGUI()
    app.run()
