import smtplib
from email.message import EmailMessage
import re

# Email configuration (you need to set these)
EMAIL_ADDRESS = ""  # 
EMAIL_PASSWORD = ""  # Your app password

def send_email(to_email, subject, message):
    """Send email using SMTP"""
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        return "Email not configured. Please set EMAIL_ADDRESS and EMAIL_PASSWORD in friday_email.py"
    
    try:
        msg = EmailMessage()
        msg.set_content(message)
        msg['Subject'] = subject
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        return f"Email sent to {to_email}"
    except Exception as e:
        return f"Email failed: {e}"

def send_email_from_text(user_input):
    """Parse natural language to send email"""
    # Extract email
    email_match = re.search(r'to\s+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', user_input, re.IGNORECASE)
    if not email_match:
        return "Please specify email address. Example: 'send email to john@example.com saying meeting at 3 PM'"
    
    to_email = email_match.group(1)
    
    # Extract message
    message_match = re.search(r'saying\s+(.+?)(?:\s+subject\s+|\s*$)', user_input, re.IGNORECASE)
    if not message_match:
        message_match = re.search(r'message\s+(.+)', user_input, re.IGNORECASE)
    
    message = message_match.group(1).strip() if message_match else "No message"
    
    # Extract subject
    subject_match = re.search(r'subject\s+(.+)', user_input, re.IGNORECASE)
    subject = subject_match.group(1).strip() if subject_match else "Message from Friday"
    
    return send_email(to_email, subject, message)