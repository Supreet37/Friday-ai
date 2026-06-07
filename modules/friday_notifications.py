from win10toast import ToastNotifier

toaster = ToastNotifier()

def show_notification(title, message, duration=5):
    """Show Windows notification"""
    try:
        toaster.show_toast(title, message, duration=duration, threaded=True)
        return f"Notification shown: {title}"
    except Exception as e:
        return f"Notification failed: {e}"

def notify_me(text):
    """Show notification from user command"""
    return show_notification("Friday AI", text)