import threading
import time
from datetime import datetime, timedelta
import re
import subprocess

# Store all reminders
reminders = []

def speak_reminder(message):
    """Speak the reminder aloud"""
    try:
        subprocess.run(['powershell', '-Command', f'Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak("Reminder: {message}")'], capture_output=True)
    except:
        print(f"🔔 REMINDER: {message}")

def check_reminders():
    """Background thread - checks every 30 seconds"""
    while True:
        now = datetime.now()
        for reminder in reminders[:]:  # iterate over copy
            if reminder['time'] <= now:
                message = reminder['message']
                print(f"\n[Friday] 🔔 Reminder: {message}")
                speak_reminder(message)
                reminders.remove(reminder)
        time.sleep(30)

# Start the reminder checker thread
reminder_thread = threading.Thread(target=check_reminders, daemon=True)
reminder_thread.start()

def parse_time(time_str):
    """
    Convert any time format to datetime object
    Supports: 5pm, 5:30 PM, 10:31pm, 22:32, 10:31, 10 PM
    """
    time_str = time_str.strip().lower()
    
    # Extract numbers and am/pm using regex
    # Matches: 10:31pm, 10:31 pm, 10pm, 10 pm, 22:32
    match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', time_str)
    
    if not match:
        return None
    
    hour = int(match.group(1))
    minute = int(match.group(2)) if match.group(2) else 0
    ampm = match.group(3)
    
    # Validate
    if hour > 23 or minute > 59:
        return None
    if hour == 0 and not ampm:
        return None
    
    # Convert 12-hour to 24-hour
    if ampm == 'pm' and hour != 12:
        hour += 12
    elif ampm == 'pm' and hour == 12:
        hour = 12
    elif ampm == 'am' and hour == 12:
        hour = 0
    elif ampm == 'am' and hour < 12:
        hour = hour
    # If no am/pm and hour <= 23, assume 24-hour format
    
    now = datetime.now()
    reminder_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    # If time already passed today, set for tomorrow
    if reminder_time <= now:
        reminder_time += timedelta(days=1)
    
    return reminder_time

def set_reminder_from_text(user_input):
    """
    Main function - called from friday_brain.py
    Parses: "remind me to call mom at 10:31 PM" or "remind me in 5 minutes to take medicine"
    """
    cmd = user_input.lower().strip()
    
    # Remove "remind me" prefix
    text = user_input.replace("remind me", "").strip()
    if text.startswith("to"):
        text = text[2:].strip()
    
    # Check for "in X minutes" format
    match = re.search(r'in (\d+) minutes?', text.lower())
    if match:
        minutes = int(match.group(1))
        # Extract message (everything before "in X minutes")
        message = re.sub(r'in \d+ minutes?', '', text.lower()).strip()
        if message.startswith("to"):
            message = message[2:].strip()
        if not message:
            message = "your reminder"
        
        reminder_time = datetime.now() + timedelta(minutes=minutes)
        reminders.append({
            'time': reminder_time,
            'message': message
        })
        return f"Reminder set for {minutes} minutes from now: '{message}'"
    
    # Check for "at" time format
    if " at " in text.lower():
        parts = re.split(r'\s+at\s+', text, maxsplit=1)
        message = parts[0].strip()
        time_str = parts[1].strip()
        
        reminder_time = parse_time(time_str)
        if reminder_time:
            reminders.append({
                'time': reminder_time,
                'message': message
            })
            return f"Reminder set for {reminder_time.strftime('%I:%M %p')}: '{message}'"
        else:
            return f"Could not understand time '{time_str}'. Try '10:31 PM', '10:31pm', '5 PM', or '22:31'"
    
    return "Please specify time. Example: 'remind me to call mom at 5 PM' or 'remind me in 10 minutes'"

def list_reminders():
    """Show all active reminders"""
    if not reminders:
        return "No active reminders, sir."
    
    result = "Active reminders:\n"
    for i, r in enumerate(reminders, 1):
        time_str = r['time'].strftime('%I:%M %p')
        result += f"{i}. {time_str} - {r['message']}\n"
    return result

def cancel_reminder(index):
    """Cancel reminder by number (1, 2, 3...)"""
    try:
        removed = reminders.pop(index - 1)
        return f"Cancelled reminder: '{removed['message']}'"
    except IndexError:
        return f"Reminder {index} not found. Use 'show reminders' to see active reminders."