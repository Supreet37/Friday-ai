import os
import glob
from difflib import get_close_matches

class AppScanner:
    def __init__(self):
        self.apps = {}
        self.scan_apps()
    
    def scan_apps(self):
        """Scan Windows Start Menu for all installed applications"""
        apps = {}
        
        # Common Start Menu locations
        search_paths = [
            os.path.join(os.environ.get('PROGRAMDATA', ''), 'Microsoft', 'Windows', 'Start Menu', 'Programs'),
            os.path.join(os.environ.get('APPDATA', ''), 'Microsoft', 'Windows', 'Start Menu', 'Programs'),
            os.path.join(os.environ.get('USERPROFILE', ''), 'Desktop'),
        ]
        
        for search_path in search_paths:
            if not os.path.exists(search_path):
                continue
            
            # Find all .lnk files (shortcuts)
            for root, dirs, files in os.walk(search_path):
                for file in files:
                    if file.endswith('.lnk'):
                        name = file.replace('.lnk', '').lower()
                        apps[name] = os.path.join(root, file)
        
        # Also add common system apps
        system_apps = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "calc": "calc.exe",
            "cmd": "cmd.exe",
            "command prompt": "cmd.exe",
            "powershell": "powershell.exe",
            "paint": "mspaint.exe",
        }
        
        for name, path in system_apps.items():
            apps[name] = path
        
        self.apps = apps
        print(f"[AppScanner] Found {len(apps)} applications")
    
    def find_app(self, command_text):
        """Find closest matching app from voice command"""
        command_lower = command_text.lower().strip()
        
        # Remove "open " prefix
        if command_lower.startswith("open "):
            command_lower = command_lower[5:].strip()
        
        # Try exact match first
        if command_lower in self.apps:
            return self.apps[command_lower]
        
        # Try close matches (handles mispronunciation)
        matches = get_close_matches(command_lower, self.apps.keys(), n=1, cutoff=0.6)
        if matches:
            print(f"[AppScanner] '{command_lower}' matched to '{matches[0]}'")
            return self.apps[matches[0]]
        
        return None
    
    def get_all_apps(self):
        """Return list of all app names"""
        return list(self.apps.keys())

# Create a global instance
scanner = AppScanner()