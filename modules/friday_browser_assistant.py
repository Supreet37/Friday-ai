import pyautogui
import easyocr
import numpy as np
import pyttsx3
import pygetwindow as gw
import time

engine = pyttsx3.init()
engine.setProperty('rate', 170)
reader = easyocr.Reader(['en'])

class BrowserAssistant:
    def __init__(self):
        pass
    
    def speak(self, text):
        try:
            engine.say(text)
            engine.runAndWait()
        except:
            print(f"[Speak] {text}")
    
    def read_screen(self):
        try:
            chrome_windows = gw.getWindowsWithTitle('Chrome')
            if not chrome_windows:
                return "❌ No Chrome window found"
            
            chrome = chrome_windows[0]
            if chrome.isMinimized:
                chrome.restore()
                time.sleep(0.5)
            chrome.activate()
            time.sleep(0.5)
            
            screenshot = pyautogui.screenshot(region=(
                chrome.left, chrome.top, chrome.width, chrome.height
            ))
            screenshot_np = np.array(screenshot)
            result = reader.readtext(screenshot_np, detail=0, paragraph=True)
            text = " ".join(result)
            
            if text and len(text) > 20:
                self.speak(text[:300])
                return f"📖 {text[:800]}"
            return "📖 No readable text found"
        except Exception as e:
            return f"❌ Error: {e}"
    
    def scroll_down(self):
        try:
            chrome_windows = gw.getWindowsWithTitle('Chrome')
            if chrome_windows:
                chrome_windows[0].activate()
                time.sleep(0.2)
            pyautogui.press('pagedown')
            return "⬇ Scrolled down"
        except:
            pyautogui.press('pagedown')
            return "⬇ Scrolled down"
    
    def scroll_up(self):
        try:
            chrome_windows = gw.getWindowsWithTitle('Chrome')
            if chrome_windows:
                chrome_windows[0].activate()
                time.sleep(0.2)
            pyautogui.press('pageup')
            return "⬆ Scrolled up"
        except:
            pyautogui.press('pageup')
            return "⬆ Scrolled up"
    
    def click_link(self, number=1):
        positions = {1: (500, 420), 2: (500, 500), 3: (500, 580)}
        x, y = positions.get(number, (500, 420))
        try:
            chrome_windows = gw.getWindowsWithTitle('Chrome')
            if chrome_windows:
                chrome_windows[0].activate()
                time.sleep(0.3)
        except:
            pass
        pyautogui.click(x, y)
        return f"🖱️ Clicked link #{number}"

browser_assistant = BrowserAssistant()