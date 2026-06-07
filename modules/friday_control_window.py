import tkinter as tk
from tkinter import scrolledtext
import threading
import time
import pyautogui
import webbrowser
import pyttsx3
import easyocr
import numpy as np
from PIL import Image, ImageTk
import os

# Initialize TTS (single instance)
engine = pyttsx3.init()
engine.setProperty('rate', 170)

# Initialize OCR
reader = easyocr.Reader(['en'])

class ControlWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Friday Control Panel")
        self.root.geometry("380x550")
        self.root.configure(bg="#1a1a2e")
        self.root.attributes('-topmost', True)
        
        self.create_avatar()
        self.create_buttons()
        self.create_log()
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-s>', lambda e: self.search())
        self.root.bind('<Control-r>', lambda e: self.read_screen())
        self.root.bind('<Control-Up>', lambda e: self.scroll_up())
        self.root.bind('<Control-Down>', lambda e: self.scroll_down())
        self.root.bind('<Control-c>', lambda e: self.click_link())
    
    def create_avatar(self):
        frame = tk.Frame(self.root, bg="#1a1a2e")
        frame.pack(pady=10)
        
        avatar_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'avatar.png')
        try:
            img = Image.open(avatar_path)
            img = img.resize((80, 80), Image.Resampling.LANCZOS)
            self.avatar_img = ImageTk.PhotoImage(img)
            avatar_label = tk.Label(frame, image=self.avatar_img, bg="#1a1a2e")
            avatar_label.pack()
        except:
            avatar_label = tk.Label(frame, text="FRIDAY", font=("Arial", 18, "bold"), 
                                    bg="#1a1a2e", fg="#00f5ff")
            avatar_label.pack()
        
        self.status_label = tk.Label(frame, text="Ready", font=("Arial", 9), 
                                      bg="#1a1a2e", fg="#00ffcc")
        self.status_label.pack()
    
    def create_buttons(self):
        btn_frame = tk.Frame(self.root, bg="#1a1a2e")
        btn_frame.pack(pady=10)
        
        self.search_entry = tk.Entry(btn_frame, width=25, font=("Arial", 10),
                                      bg="#0f0f1a", fg="white", insertbackground="white")
        self.search_entry.pack(pady=5)
        self.search_entry.insert(0, "aiml notes")
        
        tk.Button(btn_frame, text="🔍 SEARCH", command=self.search,
                  bg="#2196F3", fg="white", width=14).pack(pady=2)
        
        tk.Button(btn_frame, text="📖 READ SCREEN", command=self.read_screen,
                  bg="#FF9800", fg="white", width=14).pack(pady=2)
        
        tk.Button(btn_frame, text="⬆ SCROLL UP", command=self.scroll_up,
                  bg="#795548", fg="white", width=14).pack(pady=2)
        
        tk.Button(btn_frame, text="⬇ SCROLL DOWN", command=self.scroll_down,
                  bg="#795548", fg="white", width=14).pack(pady=2)
        
        tk.Button(btn_frame, text="🖱️ CLICK FIRST LINK", command=self.click_link,
                  bg="#9C27B0", fg="white", width=14).pack(pady=2)
    
    def create_log(self):
        log_frame = tk.Frame(self.root, bg="#1a1a2e")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(log_frame, text="Activity Log", bg="#1a1a2e", fg="#888").pack()
        
        self.log_area = scrolledtext.ScrolledText(log_frame, height=10,
                                                   bg="#0f0f1a", fg="#00ffcc", wrap=tk.WORD, font=("Arial", 8))
        self.log_area.pack(fill=tk.BOTH, expand=True)
    
    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_area.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_area.see(tk.END)
        self.status_label.config(text=message[:25])
    
    def speak(self, text):
        try:
            engine.say(text)
            engine.runAndWait()
        except:
            self.log(f"Speak: {text[:50]}...")
    
    def search(self):
        query = self.search_entry.get()
        if not query:
            query = "aiml notes"
        
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(search_url)
        self.log(f"Searched: {query}")
        self.speak(f"Searching for {query}")
    
    def read_screen(self):
        try:
            self.log("Reading screen...")
            import pygetwindow as gw
            chrome_windows = gw.getWindowsWithTitle('Chrome')
            if not chrome_windows:
                self.speak("No Chrome window found")
                return
            
            chrome = chrome_windows[0]
            screenshot = pyautogui.screenshot(region=(
                chrome.left, chrome.top, chrome.width, chrome.height
            ))
            screenshot_np = np.array(screenshot)
            result = reader.readtext(screenshot_np, detail=0, paragraph=True)
            text = " ".join(result)
            
            if text and len(text) > 20:
                self.log(f"Read {len(text)} characters")
                self.speak(text[:400])
            else:
                self.log("No text found")
                self.speak("No readable text found")
        except Exception as e:
            self.log(f"Error: {e}")
    
    def scroll_up(self):
        pyautogui.press('pageup')
        self.log("Scrolled up")
        self.speak("Scrolling up")
    
    def scroll_down(self):
        pyautogui.press('pagedown')
        self.log("Scrolled down")
        self.speak("Scrolling down")
    
    def click_link(self):
        pyautogui.click(500, 420)
        self.log("Clicked first link")
        self.speak("Clicked first link")
    
    def run(self):
        self.root.mainloop()

# Global instance
control_window = None

def start_control_window():
    global control_window
    if control_window is None:
        control_window = ControlWindow()
        threading.Thread(target=control_window.run, daemon=True).start()
    return "Control window opened"

def stop_control_window():
    global control_window
    if control_window:
        control_window.root.quit()
        control_window = None
    return "Control window closed"