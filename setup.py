"""
Setup script for building Activity Tracker as a standalone macOS app
Uses py2app to create a .app bundle
"""

from setuptools import setup

APP = ['activity_tracker.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'packages': ['tkinter', 'pynput', 'PIL', 'csv', 'datetime'],
    'includes': ['AppKit', 'Quartz'],
    'excludes': ['matplotlib', 'numpy', 'scipy'],
    'plist': {
        'CFBundleName': 'Activity Tracker',
        'CFBundleDisplayName': 'Activity Tracker',
        'CFBundleGetInfoString': 'Track keyboard and mouse activity',
        'CFBundleIdentifier': 'com.traversable.activitytracker',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': 'Free for personal use',
        # Request accessibility permissions
        'NSAppleEventsUsageDescription': 'This app needs to monitor keyboard and mouse input to track activity.',
    },
    'iconfile': 'ref/TDT-logo-white-circle.icns',  # Custom icon!
}

setup(
    name='Activity Tracker',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
