import os
import shutil
from datetime import datetime

def create_folder(folder_name):
    """Create a new folder on Desktop"""
    desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
    folder_path = os.path.join(desktop, folder_name)
    try:
        os.makedirs(folder_path, exist_ok=True)
        return f"Created folder: {folder_name} on Desktop"
    except Exception as e:
        return f"Failed to create folder: {e}"

def delete_file(file_name):
    """Delete a file from Desktop"""
    desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
    file_path = os.path.join(desktop, file_name)
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return f"Deleted file: {file_name}"
        return f"File not found: {file_name}"
    except Exception as e:
        return f"Delete failed: {e}"

def list_files():
    """List files on Desktop"""
    desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
    try:
        files = [f for f in os.listdir(desktop) if os.path.isfile(os.path.join(desktop, f))]
        if files:
            return "Files on Desktop:\n" + "\n".join(files[:10])
        return "No files on Desktop"
    except Exception as e:
        return f"List failed: {e}"