import pyperclip
import subprocess

def copy_to_clipboard(text):
    """Copy text to clipboard"""
    try:
        pyperclip.copy(text)
        return f"Copied: {text[:50]}..." if len(text) > 50 else f"Copied: {text}"
    except Exception as e:
        return f"Copy failed: {e}"

def paste_from_clipboard():
    """Get text from clipboard"""
    try:
        text = pyperclip.paste()
        if text:
            return f"Clipboard contains: {text[:200]}"
        return "Clipboard is empty"
    except Exception as e:
        return f"Paste failed: {e}"

def clear_clipboard():
    """Clear clipboard"""
    try:
        pyperclip.copy("")
        return "Clipboard cleared"
    except Exception as e:
        return f"Clear failed: {e}"