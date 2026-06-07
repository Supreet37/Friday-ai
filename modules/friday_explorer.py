import subprocess
import os
import pygetwindow as gw
import pyautogui
import time

class FridayExplorer:
    
    def get_active_explorer_path(self):
        """Get the path of the active File Explorer window"""
        try:
            # Focus on Explorer window
            explorer_windows = gw.getWindowsWithTitle('File Explorer')
            if not explorer_windows:
                # Try to find any Explorer window
                explorer_windows = [w for w in gw.getAllWindows() if 'Explorer' in w.title]
            
            if explorer_windows:
                explorer_windows[0].activate()
                time.sleep(0.5)
                # Press Ctrl+L to focus address bar
                pyautogui.hotkey('ctrl', 'l')
                time.sleep(0.3)
                pyautogui.hotkey('ctrl', 'c')
                time.sleep(0.3)
                # Get path from clipboard
                import pyperclip
                current_path = pyperclip.paste()
                return current_path
            return None
        except Exception as e:
            print(f"Error getting path: {e}")
            return None
    
    def create_folder_here(self, folder_name):
        """Create folder in currently open Explorer window"""
        try:
            current_path = self.get_active_explorer_path()
            if not current_path:
                return "Please open a File Explorer window first, sir."
            
            folder_path = os.path.join(current_path, folder_name)
            os.makedirs(folder_path, exist_ok=True)
            
            # Refresh Explorer
            pyautogui.hotkey('ctrl', 'r')
            
            return f"Created folder '{folder_name}' in {current_path}, sir."
        except Exception as e:
            return f"Failed: {e}"
    
    def open_drive(self, drive_letter):
        """Open a drive in File Explorer"""
        drive = f"{drive_letter}:\\"
        if os.path.exists(drive):
            subprocess.Popen(f'explorer "{drive}"')
            return f"Opening {drive_letter}: drive, sir."
        return f"Drive {drive_letter}: not found."

friday_explorer = FridayExplorer()