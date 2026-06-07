import os
import ctypes
import subprocess
from modules.friday_app_scanner import scanner

def open_app(command):
    print(f"[DEBUG] open_app received: '{command}'")
    cmd_lower = command.lower().strip()
    
    # Remove "open " prefix if present
    if cmd_lower.startswith("open "):
        cmd_lower = cmd_lower[5:].strip()
    
    # List of websites to open in browser (keep as is)
    websites = ["youtube", "pinterest", "facebook", "instagram", "twitter", "x.com", "reddit", "amazon", "flipkart", "github", "gmail", "drive", "maps", "news", "google"]
    
    for site in websites:
        if site in cmd_lower:
            url = f"https://www.{site}.com"
            if site == "x.com":
                url = "https://x.com"
            os.system(f"start chrome.exe {url}")
            return f"Opening {cmd_lower} in Chrome, sir."
    
    # ========== NEW: Use dynamic app scanner ==========
    app_path = scanner.find_app(command)
    if app_path:
        try:
            if app_path.endswith('.exe'):
                os.system(f"start {app_path}")
            else:
                os.system(f"start {app_path}")
            return f"Opening {cmd_lower}, sir."
        except Exception as e:
            print(f"Open error: {e}")
    
    # Fallback: try direct command
    try:
        os.system(f"start {cmd_lower}")
        return f"Opening {cmd_lower}, sir."
    except:
        return f"Could not find {cmd_lower}"

# Keep all other functions (volume, shutdown, etc.) unchanged
def volume_up():
    ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0)
    return "Volume increased"

def volume_down():
    ctypes.windll.user32.keybd_event(0xAE, 0, 0, 0)
    return "Volume decreased"

def mute():
    ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)
    return "Volume muted"

def shutdown_pc():
    os.system("shutdown /s /t 10")
    return "Shutting down in 10 seconds"

def restart_pc():
    os.system("shutdown /r /t 10")
    return "Restarting in 10 seconds"

def sleep_pc():
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    return "Going to sleep"

def lock_screen():
    ctypes.windll.user32.LockWorkStation()
    return "Screen locked"