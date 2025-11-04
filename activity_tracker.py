"""
Cross-Platform Activity Tracker - Compact & Customizable
Tracks keyboard and mouse activity by application

Dependencies:
pip install pynput pillow
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import threading
import csv
import os
from collections import defaultdict
import glob
import subprocess
from PIL import Image, ImageTk

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
    print(f"Warning: Could not import pynput or required libraries: {e}")
    PYNPUT_AVAILABLE = False

# Platform-specific imports
import platform
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
BUTTON_STOP_BG = "#9C2D2D"  
BUTTON_START_BG = "#2D9C64"  
BUTTON_MODE_BG = "#9C642D"  
BUTTON_FOLDER_BG = "#2D649C"  
BUTTON_TEXT_COLOR = "#123456"  # Button text color

# Text colors
STATUS_TRACKING_COLOR = "#FFFFFF"  # "TRACKING" text color
STATUS_STOPPED_COLOR = "#FFFFFF"   # "STOPPED" text color  
STATS_TEXT_COLOR = "#FFFFFF"       # Stats text color (time & events)

# Font settings
FONT_FAMILY = "Arial"
FONT_SIZE_STATUS = 10
FONT_SIZE_BUTTON = 9

# ================================================


class ActivityTracker:
    """Main class for tracking keyboard and mouse activity"""
    
    def __init__(self, autosave_interval=60):  # Changed to 60 seconds (1 minute)
        self.tracking = False
        self.global_mode = False  # False = app-specific, True = global
        self.data_folder = 'activity_data'
        self.autosave_interval = autosave_interval  # seconds between auto-saves
        self.last_save_time = datetime.now()
        
        # Create data folder if it doesn't exist
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
        
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
        if self.global_mode:
            return "Global"
        
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
        """Record an activity event"""
        if not self.tracking:
            return
        
        event = {
            'timestamp': datetime.now().isoformat(),
            'app': self.get_active_application(),
            'event_type': event_type,
            'key': key if key else event_type
        }
        self.session_events.append(event)
        self.event_count += 1
        
        # Print every event to terminal for feedback
        print(f"[{event['app']}] {event_type}: {key if key else 'N/A'}")
        
        # Auto-save if interval has passed
        if (datetime.now() - self.last_save_time).total_seconds() >= self.autosave_interval:
            self.save_session()
            self.last_save_time = datetime.now()
            print(f">>> Auto-saved: {len(self.session_events)} events | File: {self.session_file} <<<")
    
    def on_key_press(self, key):
        """Callback for keyboard events"""
        try:
            # Convert key to string representation
            if hasattr(key, 'char') and key.char is not None:
                key_str = key.char
            else:
                key_str = str(key).replace('Key.', '')
            
            self.record_event('keystroke', key_str)
        except Exception as e:
            # Silently ignore errors to prevent spam
            pass
    
    def on_click(self, x, y, button, pressed):
        """Callback for mouse click events"""
        if pressed:  # Only record on press, not release
            button_str = str(button).replace('Button.', '')
            self.record_event('click', button_str)
    
    def start_tracking(self):
        """Start tracking (or restart with new session)"""
        # Start new session
        self.event_count = 0
        self.session_start = datetime.now()
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.session_file = os.path.join(self.data_folder, f'session_{self.session_id}.csv')
        self.session_events = []
        self.tracking = True
        
        print(f"Tracking started... Session ID: {self.session_id}")
        
        # Only create listeners once on first start
        if not self.listeners_started and PYNPUT_AVAILABLE:
            print("Creating listeners for the first time...")
            
            # Start keyboard monitoring - ignore the trust error
            try:
                # Create listener without checking trust status
                self.keyboard_listener = keyboard.Listener(
                    on_press=self.on_key_press,
                    suppress=False
                )
                # Start in a thread so errors don't crash the app
                keyboard_thread = threading.Thread(target=self.keyboard_listener.start, daemon=True)
                keyboard_thread.start()
                
                # Give it a moment
                import time
                time.sleep(0.3)
                print(f"✓ Keyboard listener started")
            except Exception as e:
                print(f"✗ Keyboard listener error (may still work): {e}")
            
            # Start mouse monitoring
            try:
                self.mouse_listener = mouse.Listener(on_click=self.on_click)
                self.mouse_listener.start()
                print(f"✓ Mouse listener started")
            except Exception as e:
                print(f"✗ Error starting mouse listener: {e}")
            
            self.listeners_started = True
        else:
            print("Listeners already running, just starting new session")
    
    def stop_tracking(self):
        """Stop tracking (but keep listeners running)"""
        self.tracking = False
        self.save_session()
        print(f"Tracking stopped. Saved {len(self.session_events)} events")
        # Note: We DON'T stop the listeners - they keep running in the background
    
    def toggle_mode(self):
        """Toggle between app-specific and global tracking"""
        self.global_mode = not self.global_mode
        return self.global_mode
    
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
            print(f"Error saving session: {e}")
            import traceback
            traceback.print_exc()
    
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
                    print(f"Warning: Could not load {session_file}: {e}")
                    continue
        except Exception as e:
            print(f"Error loading sessions: {e}")
        
        return all_events
    
    def get_session_count(self):
        """Get total number of session files"""
        try:
            session_files = glob.glob(os.path.join(self.data_folder, 'session_*.csv'))
            return len(session_files)
        except Exception as e:
            print(f"Error counting sessions: {e}")
            return 0


class ActivityTrackerGUI:
    """Compact customizable GUI for the Activity Tracker"""
    
    def __init__(self):
        self.tracker = ActivityTracker(autosave_interval=30)
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Activity Tracker")
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
                print(f"Loaded background image with overlay: {BG_IMAGE_PATH}")
            except Exception as e:
                print(f"Could not load background image: {e}")
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
                
                # Create buttons with customizable colors
                button_y = height//2
                button_spacing = 90
                start_x = width//2 - button_spacing
                
                self.toggle_btn = tk.Button(self.root, text="STOP",
                                            command=self.toggle_tracking,
                                            font=(FONT_FAMILY, FONT_SIZE_BUTTON, 'bold'),
                                            bg=BUTTON_STOP_BG, fg=BUTTON_TEXT_COLOR,
                                            width=8, height=1, 
                                            relief=tk.FLAT, bd=0)
                self.canvas.create_window(start_x, button_y, window=self.toggle_btn)
                
                self.mode_btn = tk.Button(self.root, text="APP",
                                         command=self.toggle_mode,
                                         font=(FONT_FAMILY, FONT_SIZE_BUTTON, 'bold'),
                                         bg=BUTTON_MODE_BG, fg=BUTTON_TEXT_COLOR,
                                         width=8, height=1,
                                         relief=tk.FLAT, bd=0)
                self.canvas.create_window(start_x + button_spacing, button_y, window=self.mode_btn)
                
                self.folder_btn = tk.Button(self.root, text="FOLDER",
                                           command=self.open_data_folder,
                                           font=(FONT_FAMILY, FONT_SIZE_BUTTON, 'bold'),
                                           bg=BUTTON_FOLDER_BG, fg=BUTTON_TEXT_COLOR,
                                           width=8, height=1,
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
                
                self.toggle_btn = tk.Button(button_frame, text="STOP",
                                            command=self.toggle_tracking,
                                            font=(FONT_FAMILY, FONT_SIZE_BUTTON, 'bold'),
                                            bg=BUTTON_STOP_BG, fg='#FFFFFF',
                                            width=8, height=1, 
                                            relief=tk.FLAT, bd=0)
                self.toggle_btn.pack(side=tk.LEFT, padx=2)
                
                self.mode_btn = tk.Button(button_frame, text="APP",
                                         command=self.toggle_mode,
                                         font=(FONT_FAMILY, FONT_SIZE_BUTTON, 'bold'),
                                         bg=BUTTON_MODE_BG, fg='#FFFFFF',
                                         width=8, height=1,
                                         relief=tk.FLAT, bd=0)
                self.mode_btn.pack(side=tk.LEFT, padx=2)
                
                self.folder_btn = tk.Button(button_frame, text="FOLDER",
                                           command=self.open_data_folder,
                                           font=(FONT_FAMILY, FONT_SIZE_BUTTON, 'bold'),
                                           bg=BUTTON_FOLDER_BG, fg='#FFFFFF',
                                           width=8, height=1,
                                           relief=tk.FLAT, bd=0)
                self.folder_btn.pack(side=tk.LEFT, padx=2)
                
                self.stats_label = tk.Label(self.main_frame, text="0m 0s | 0 events", 
                                            font=(FONT_FAMILY, 7), 
                                            bg=BG_COLOR, fg='#000000')
                self.stats_label.pack(pady=5)
            
        except Exception as e:
            print(f"Error creating UI: {e}")
            import traceback
            traceback.print_exc()
    
    def _darken_color(self, hex_color):
        """Darken a hex color by 20% for active state"""
        try:
            hex_color = hex_color.lstrip('#')
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            r, g, b = int(r * 0.8), int(g * 0.8), int(b * 0.8)
            return f'#{r:02x}{g:02x}{b:02x}'
        except:
            return hex_color
    
    def toggle_tracking(self):
        """Toggle tracking on/off"""
        try:
            if self.tracker.tracking:
                # Stop current tracking
                self.tracker.stop_tracking()
                self.toggle_btn.config(text="START", bg=BUTTON_START_BG, fg=BUTTON_TEXT_COLOR)
                self.status_label.config(text="STOPPED", fg=STATUS_STOPPED_COLOR)
            else:
                # Start new tracking session
                import time
                time.sleep(0.2)
                
                # Start tracking in a new thread
                self.tracking_thread = threading.Thread(
                    target=self.tracker.start_tracking, daemon=True)
                self.tracking_thread.start()
                
                self.toggle_btn.config(text="STOP", bg=BUTTON_STOP_BG, fg=BUTTON_TEXT_COLOR)
                self.status_label.config(text="TRACKING", fg=STATUS_TRACKING_COLOR)
        except Exception as e:
            print(f"Error toggling tracking: {e}")
            import traceback
            traceback.print_exc()
    
    def toggle_mode(self):
        """Toggle between app-specific and global mode"""
        is_global = self.tracker.toggle_mode()
        if is_global:
            self.mode_btn.config(text="GLOBAL")
            print("Switched to Global mode")
        else:
            self.mode_btn.config(text="APP")
            print("Switched to App-Specific mode")
    
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
            print(f"Opened folder: {folder_path}")
        except Exception as e:
            print(f"Could not open folder: {e}")
    
    def start_status_updates(self):
        """Start the status update loop"""
        self.update_status()
    
    def update_status(self):
        """Update status display"""
        try:
            if self.tracker.tracking:
                session_duration = (datetime.now() - self.tracker.session_start).total_seconds()
                minutes = int(session_duration // 60)
                seconds = int(session_duration % 60)
                stats_text = f"{minutes}m {seconds}s | {self.tracker.event_count} events"
            else:
                all_events = self.tracker.load_all_sessions()
                stats_text = f"Total: {len(all_events):,} events"
            
            if hasattr(self, 'stats_label') and self.stats_label.winfo_exists():
                self.stats_label.config(text=stats_text)
        except Exception as e:
            print(f"Status update error: {e}")
        
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
        self.tracker.stop_tracking()
        self.root.destroy()


if __name__ == "__main__":
    print("Activity Tracker Started")
    print("=" * 40)
    app = ActivityTrackerGUI()
    app.run()
