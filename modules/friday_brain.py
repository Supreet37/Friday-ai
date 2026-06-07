import ollama
import json
import os
import time
import re
import webbrowser
from modules.friday_playwright import friday_browser
from modules.friday_email import send_email_from_text
from modules.friday_filemanager import create_folder, delete_file, list_files
from modules.friday_notifications import notify_me
from modules.friday_websearch import web_search
from modules.friday_system import open_app, volume_up, volume_down, mute, shutdown_pc, restart_pc, sleep_pc, lock_screen
from modules.friday_weather import get_weather
from modules.friday_screenshot import take_screenshot
from modules.friday_systeminfo import get_ram_info, get_battery_info, get_cpu_info, get_system_summary
from modules.friday_reminder import set_reminder_from_text, list_reminders, cancel_reminder
from modules.friday_whatsapp import send_whatsapp_from_text
from modules.friday_clipboard import copy_to_clipboard, paste_from_clipboard, clear_clipboard
from modules.friday_food import friday_food
from modules.friday_voice_out import FridayVoiceOut
from modules.friday_browser_assistant import browser_assistant
from modules.friday_word_writer import write_from_text
from modules.friday_developer import  open_vscode, open_vscode_folder
from modules.friday_developer import detect_language_and_generate, create_file, read_file, run_python_file
from modules.friday_explorer import friday_explorer
from modules.friday_email import write_email_from_text

# Create voice instance
voice = FridayVoiceOut()

class FridayBrain:
    def __init__(self):
        self.model = "qwen2.5:1.5b"
        self.detected_language = "en"
        self.system_prompt = {"role": "system", "content": "You are Friday, a friendly AI assistant. Keep responses short."}
        self.messages = [self.system_prompt]
        self.load_history()
    
    def load_history(self):
        history_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'memory', 'chat_history.json')
        if os.path.exists(history_path):
            try:
                with open(history_path, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    if saved:
                        self.messages = [self.system_prompt] + saved
            except:
                pass
    
    def save_history(self):
        history_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'memory', 'chat_history.json')
        save_messages = [m for m in self.messages if m['role'] != 'system']
        with open(history_path, 'w', encoding='utf-8') as f:
            json.dump(save_messages, f, ensure_ascii=False, indent=2)
    
    def detect_language_simple(self, text):
        return "hi" if any('\u0900' <= c <= '\u097F' for c in text) else "en"
    
    def chat(self, user_input):
        self.detected_language = self.detect_language_simple(user_input)
        cmd = user_input.lower().strip()

        # STOP WORD
        if cmd in ["stop", "shut up", "be quiet", "stop talking", "stop speaking"]:
            return voice.stop_speaking()

        # ============================================================
        # FILE EXPLORER - Open Drives (CHECK FIRST - BEFORE WEBSITE)
        # ============================================================
        if cmd.startswith("open ") and len(cmd) <= 6 and cmd[5:].strip() in ["c", "d", "e", "f", "g", "h"]:
            drive = cmd[5:].strip()
            return friday_explorer.open_drive(drive)
        
        if "open desktop" in cmd:
            return friday_explorer.open_desktop()
        
        if "open documents" in cmd:
            return friday_explorer.open_documents()
        
        if "open downloads" in cmd:
            return friday_explorer.open_downloads()
        
        if "create folder" in cmd:
            folder_name = cmd.replace("create folder", "").strip()
            if folder_name:
                return friday_explorer.create_folder(folder_name)
            return "What folder should I create? Example: 'create folder MyProjects'"
        
        if "open folder" in cmd:
            folder_name = cmd.replace("open folder", "").strip()
            if folder_name:
                if os.path.exists(folder_name):
                    return friday_explorer.open_folder(folder_name)
                else:
                    desktop_folder = os.path.join(os.environ['USERPROFILE'], 'Desktop', folder_name)
                    if os.path.exists(desktop_folder):
                        return friday_explorer.open_folder(desktop_folder)
                    return f"Folder '{folder_name}' not found"
            return "What folder should I open?"
        
        if "go up" in cmd or "parent folder" in cmd:
            return friday_explorer.go_up()

        # ============================================================
        # READ SCREEN
        # ============================================================
        if "read screen" in cmd or "read this page" in cmd or "the screen" in cmd or "read the screen" in cmd:
            return browser_assistant.read_screen()
        
        # ============================================================
        # CLICK LINK
        # ============================================================
        if "click link" in cmd or "click on link" in cmd:
            number = 1
            if "link 2" in cmd or "second link" in cmd:
                number = 2
            elif "link 3" in cmd or "third link" in cmd:
                number = 3
            return browser_assistant.click_link(number)
        
        # ============================================================
        # SCROLL
        # ============================================================
        if "scroll down" in cmd:
            return browser_assistant.scroll_down()
        
        if "scroll up" in cmd:
            return browser_assistant.scroll_up()
        
        # ============================================================
        # AMAZON SEARCH
        # ============================================================
        if "amazon" in cmd and "search" in cmd:
            query = cmd.replace("search", "").replace("amazon", "").replace("for", "").strip()
            search_url = f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
            webbrowser.open(search_url)
            return f"Searching Amazon for {query}"
        
        # ============================================================
        # FLIPKART SEARCH
        # ============================================================
        if "flipkart" in cmd and "search" in cmd:
            query = cmd.replace("search", "").replace("flipkart", "").replace("for", "").strip()
            search_url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(search_url)
            return f"Searching Flipkart for {query}"
        
        # ============================================================
        # GENERAL SEARCH - Opens Google
        # ============================================================
        if "search for" in cmd or cmd.startswith("search "):
            query = cmd.replace("search for", "").replace("search", "").strip()
            if query:
                search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                webbrowser.open(search_url)
                return f"Searching Google for {query}"
            return "What should I search for?"
        
        # ============================================================
        # OPEN WEBSITE (Simple)
        # ============================================================
        if cmd.startswith("open "):
            site = cmd[5:].strip()
            if "." in site:
                url = f"https://{site}"
            else:
                url = f"https://www.{site}.com"
            webbrowser.open(url)
            return f"Opening {site}"
        
        # ============================================================
        # SWIGGY FOOD ORDERING
        # ============================================================
        if cmd.startswith("swiggy search for ") or ("swiggy" in cmd and "search" in cmd):
            query = cmd.replace("swiggy search for", "").replace("swiggy", "").replace("search", "").strip()
            return friday_food.swiggy_search(query)
        
        if "swiggy add to cart" in cmd:
            return friday_food.swiggy_add_to_cart()
        
        # ============================================================
        # ZOMATO FOOD ORDERING
        # ============================================================
        if cmd.startswith("zomato search for ") or ("zomato" in cmd and "search" in cmd):
            query = cmd.replace("zomato search for", "").replace("zomato", "").replace("search", "").strip()
            return friday_food.zomato_search(query)
        
        if "zomato add to cart" in cmd:
            return friday_food.zomato_add_to_cart()
        
        # ============================================================
        # WORD WRITER - Opens Word and types
        # ============================================================
        if "write" in cmd and ("word" in cmd or "in word" in cmd):
            return write_from_text(user_input)
        
        if "write email" in cmd:
            return write_from_text(user_input)
        
        if "write letter" in cmd:
            return write_from_text(user_input)
        
        # ============================================================
        # WEATHER
        # ============================================================
        if "weather" in cmd or "temperature" in cmd:
            city = "your location"
            for word in ["in", "at", "for"]:
                if word in cmd:
                    parts = cmd.split(word, 1)
                    if len(parts) > 1:
                        city = parts[1].strip()
                        break
            return get_weather(city)
        
        # ============================================================
        # EMAIL WRITER - Opens Notepad with draft
        # ============================================================
        if "write email" in cmd:
            return write_email_from_text(user_input)
        
        # ============================================================
        # SCREENSHOT
        # ============================================================
        if "screenshot" in cmd or "take a screenshot" in cmd:
            return take_screenshot()
        
        # ============================================================
        # SYSTEM INFO
        # ============================================================
        if "ram" in cmd or "memory" in cmd:
            return f"RAM {get_ram_info()}"
        if "battery" in cmd:
            return get_battery_info()
        if "cpu" in cmd or "processor" in cmd:
            return f"CPU usage {get_cpu_info()}"
        if "system info" in cmd or "pc status" in cmd:
            return get_system_summary()
        
        # ============================================================
        # REMINDERS
        # ============================================================
        if "remind me" in cmd:
            return set_reminder_from_text(user_input)
        if "show reminders" in cmd or "list reminders" in cmd:
            return list_reminders()
        if "cancel reminder" in cmd:
            match = re.search(r'cancel reminder (\d+)', cmd)
            if match:
                return cancel_reminder(int(match.group(1)))
            return "Say 'cancel reminder 1'"
        
        # ============================================================
        # WHATSAPP
        # ============================================================
        if "whatsapp" in cmd or ("send" in cmd and "message" in cmd):
            return send_whatsapp_from_text(user_input)
        
        # ============================================================
        # EMAIL
        # ============================================================
        if "send email" in cmd:
            return send_email_from_text(user_input)
        
        # ============================================================
        # NOTIFICATIONS
        # ============================================================
        if "notify me" in cmd or "show notification" in cmd:
            text = user_input.replace("notify me", "").replace("show notification", "").strip()
            return notify_me(text) if text else "What should I notify you about?"
        
        # ============================================================
        # CLIPBOARD
        # ============================================================
        if "copy" in cmd and ("this" in cmd or "to clipboard" in cmd):
            text = user_input.replace("copy", "").replace("to clipboard", "").strip()
            return copy_to_clipboard(text) if text else "What should I copy?"
        if "paste" in cmd or "what's in clipboard" in cmd:
            return paste_from_clipboard()
        if "clear clipboard" in cmd:
            return clear_clipboard()
        
        # ============================================================
        # FILE MANAGER
        # ============================================================
        if "create folder" in cmd:
            folder_name = user_input.replace("create folder", "").strip()
            return create_folder(folder_name) if folder_name else "What folder to create?"
        if "delete file" in cmd:
            file_name = user_input.replace("delete file", "").strip()
            return delete_file(file_name) if file_name else "What file to delete?"
        if "list files" in cmd or "show files" in cmd:
            return list_files()
        
        # ============================================================
        # DEVELOPER - VS CODE
        # ============================================================
        if "open vs code" in cmd or "open vscode" in cmd:
            return open_vscode()
        if "open folder" in cmd and "vs code" in cmd:
            folder = user_input.replace("open folder", "").replace("in vs code", "").replace("in vscode", "").strip()
            return open_vscode_folder(folder) if folder else "What folder to open?"
        
        # ============================================================
        # DEVELOPER - CODE GENERATION
        # ============================================================
        if any(word in cmd for word in ["write", "generate", "create code", "script for", "program for"]):
            if any(lang in cmd for lang in ["python", "html", "css", "javascript", "js", "java", "c", "react", "cpp", "go", "rust", "php", "ruby", "swift", "kotlin", "typescript"]):
                return detect_language_and_generate(user_input)
        
        # ============================================================
        # DEVELOPER - FILE OPERATIONS
        # ============================================================
        if "create file" in cmd:
            filename = user_input.replace("create file", "").strip()
            return create_file(filename) if filename else "What file to create?"
        if "read file" in cmd:
            filename = user_input.replace("read file", "").strip()
            return read_file(filename) if filename else "What file to read?"
        if "run file" in cmd or "execute file" in cmd:
            filename = user_input.replace("run file", "").replace("execute file", "").strip()
            return run_python_file(filename) if filename else "What file to run?"
        
        # ============================================================
        # VOLUME CONTROL
        # ============================================================
        if "volume up" in cmd or "increase volume" in cmd:
            return volume_up()
        if "volume down" in cmd or "decrease volume" in cmd:
            return volume_down()
        if "mute" in cmd:
            return mute()
        
        # ============================================================
        # SYSTEM CONTROL
        # ============================================================
        if "shutdown" in cmd:
            return shutdown_pc()
        if "restart" in cmd:
            return restart_pc()
        if "sleep" in cmd:
            return sleep_pc()
        if "lock screen" in cmd:
            return lock_screen()
        
        # ============================================================
        # WEB SEARCH (DuckDuckGo - Text Only)
        # ============================================================
        if any(word in cmd for word in ["search", "google", "news", "find", "look up"]):
            query = user_input
            for prefix in ["search for", "search", "google", "find", "look up"]:
                if cmd.startswith(prefix):
                    query = user_input[len(prefix):].strip()
                    break
            return web_search(query)
        
        # ============================================================
        # OPEN APP (Fallback)
        # ============================================================
        if cmd.startswith("open "):
            return open_app(user_input)
        
        # ============================================================
        # NORMAL CHAT WITH OLLAMA
        # ============================================================
        self.messages.append({"role": "user", "content": user_input})
        
        if len(self.messages) > 21:
            self.messages = [self.messages[0]] + self.messages[-20:]
        
        try:
            response = ollama.chat(model=self.model, messages=self.messages)
            assistant_response = response["message"]["content"]
            self.messages.append({"role": "assistant", "content": assistant_response})
            self.save_history()
            return assistant_response
        except Exception as e:
            return f"Error: {e}"
    
    def clear_history(self):
        self.messages = [self.system_prompt]
        self.save_history()