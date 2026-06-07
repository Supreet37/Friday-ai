import pyautogui
import easyocr
import numpy as np
import pygetwindow as gw
import time

reader = easyocr.Reader(['en'])

class FridayOCR:
    def __init__(self):
        print("[OCR] Ready")
    
    def get_chrome_window(self):
        """Get the active Chrome window"""
        chrome_windows = gw.getWindowsWithTitle('Chrome')
        if chrome_windows:
            chrome = chrome_windows[0]
            if chrome.isMinimized:
                chrome.restore()
            chrome.activate()
            time.sleep(0.5)
            return chrome
        return None
    
    def read_screen(self):
        """Read text from Chrome window only"""
        try:
            chrome = self.get_chrome_window()
            if not chrome:
                return "No Chrome window found. Please open Chrome first."
            
            # Take screenshot of only Chrome window
            screenshot = pyautogui.screenshot(region=(
                chrome.left, chrome.top, chrome.width, chrome.height
            ))
            screenshot_np = np.array(screenshot)
            result = reader.readtext(screenshot_np, detail=0, paragraph=True)
            text = " ".join(result)
            return text if text else "No text found in Chrome window"
        except Exception as e:
            return f"OCR error: {e}"
    
    def click_text(self, search_text):
        """Find and click text in Chrome window"""
        try:
            chrome = self.get_chrome_window()
            if not chrome:
                return "No Chrome window found"
            
            screenshot = pyautogui.screenshot(region=(
                chrome.left, chrome.top, chrome.width, chrome.height
            ))
            screenshot_np = np.array(screenshot)
            results = reader.readtext(screenshot_np)
            
            for (bbox, text, confidence) in results:
                if search_text.lower() in text.lower():
                    x = chrome.left + int((bbox[0][0] + bbox[2][0]) / 2)
                    y = chrome.top + int((bbox[0][1] + bbox[2][1]) / 2)
                    pyautogui.click(x, y)
                    return f"Clicked on '{text}'"
            return f"Could not find '{search_text}'"
        except Exception as e:
            return f"Click error: {e}"
    
    def search_on_screen(self, search_text):
        """Search for text in Chrome window"""
        try:
            chrome = self.get_chrome_window()
            if not chrome:
                return []
            
            screenshot = pyautogui.screenshot(region=(
                chrome.left, chrome.top, chrome.width, chrome.height
            ))
            screenshot_np = np.array(screenshot)
            results = reader.readtext(screenshot_np)
            
            matches = []
            for (bbox, text, confidence) in results:
                if search_text.lower() in text.lower():
                    matches.append({'text': text, 'confidence': confidence})
            return matches
        except Exception as e:
            return []

friday_ocr = FridayOCR()