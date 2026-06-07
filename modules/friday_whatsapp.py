import pywhatkit as kit
import re
import json
import os
import pyautogui
import time

def load_contacts():
    contacts_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'contacts.json')
    if os.path.exists(contacts_path):
        with open(contacts_path, 'r') as f:
            return json.load(f)
    return {}

def send_whatsapp_message(phone_number, message):
    try:
        phone_number = str(phone_number).strip()
        message = str(message).strip()
        
        # Send the message
        kit.sendwhatmsg_instantly(phone_number, message, wait_time=25, tab_close=False)
        
        # Wait and press Enter to send
        time.sleep(3)
        pyautogui.press('enter')
        
        return "WhatsApp message sent successfully"
    except Exception as e:
        return f"WhatsApp error: {e}"

def send_whatsapp_from_text(user_input):
    contacts = load_contacts()
    cmd_lower = user_input.lower()
    
    for name in contacts.keys():
        if name in cmd_lower:
            contact = contacts[name]
            number = str(contact.get('number', '')).strip()
            country_code = str(contact.get('country_code', '91')).strip()
            number = re.sub(r'\D', '', number)
            country_code = re.sub(r'\D', '', country_code)
            full_number = f"+{country_code}{number}"
            
            message_match = re.search(r'saying\s+(.+)', user_input, re.IGNORECASE)
            if message_match:
                message = message_match.group(1).strip()
                return send_whatsapp_message(full_number, message)
            else:
                return f"What should I say to {name}? Use 'saying'"
    
    return "Contact not found. Add to config/contacts.json"