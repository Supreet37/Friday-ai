import pyautogui
import os
from datetime import datetime

def take_screenshot():
    """Take screenshot and save to desktop"""
    try:
        # Create screenshots folder on desktop if not exists
        desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        screenshots_folder = os.path.join(desktop, 'Friday_Screenshots')
        
        if not os.path.exists(screenshots_folder):
            os.makedirs(screenshots_folder)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = os.path.join(screenshots_folder, filename)
        
        # Take screenshot
        screenshot = pyautogui.screenshot()
        screenshot.save(filepath)
        
        return "Screenshot taken, Sup"
        
    except Exception as e:
        return f"Screenshot failed to be taken"