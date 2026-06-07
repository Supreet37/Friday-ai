import os
import subprocess
import ollama
import re

def generate_code(language, task, filename):
    """Generate code in any language using Ollama and open in VS Code"""
    
    prompt = f"""Generate only {language} code for this task. No explanations. No markdown. Just the raw code.

Task: {task}

Output only the {language} code, nothing else."""
    
    try:
        response = ollama.chat(model="qwen2.5:1.5b", messages=[{"role": "user", "content": prompt}])
        code = response["message"]["content"]
        
        # Clean code (remove markdown if present)
        code = re.sub(r'```\w*\n?', '', code)
        code = re.sub(r'```', '', code)
        code = code.strip()
        
        desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        filepath = os.path.join(desktop, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(code)
        
        # Open the file with default application
        os.startfile(filepath)
        
        return f"Generated {language} code saved to {filename} and opened, sir."
    except Exception as e:
        return f"Code generation failed: {e}"

def detect_language_and_generate(user_input):
    """Parse user input to detect language and task"""
    cmd = user_input.lower()
    
    languages = {
        "python": ".py",
        "html": ".html",
        "css": ".css",
        "javascript": ".js",
        "js": ".js",
        "java": ".java",
        "c": ".c",
        "react": ".jsx",
        "cpp": ".cpp",
        "c++": ".cpp",
        "go": ".go",
        "rust": ".rs",
        "php": ".php",
        "ruby": ".rb",
        "swift": ".swift",
        "kotlin": ".kt",
        "typescript": ".ts",
        "ts": ".ts",
    }
    
    detected_lang = None
    extension = ".txt"
    
    for lang, ext in languages.items():
        if lang in cmd:
            detected_lang = lang
            extension = ext
            break
    
    if not detected_lang:
        return "Which language? Example: 'write HTML code for a login form' or 'write Python code to sort a list'"
    
    # Extract task - remove command words and language
    task = user_input
    remove_words = ["write", "generate", "create", "code for", "script for", "program for", detected_lang]
    for word in remove_words:
        task = task.replace(word, "")
    task = task.strip()
    
    if not task:
        task = "sample code"
    
    # Generate filename
    filename = f"{task[:20].replace(' ', '_')}{extension}"
    filename = re.sub(r'[^a-zA-Z0-9_.-]', '', filename)
    
    return generate_code(detected_lang, task, filename)

def open_vscode():
    """Open VS Code"""
    vscode_paths = [
        r"C:\Program Files\Microsoft VS Code\Code.exe",
        r"C:\Users\Lenovo\AppData\Local\Programs\Microsoft VS Code\Code.exe",
        r"C:\Users\Lenovo\AppData\Local\Programs\Microsoft VS Code Insiders\Code - Insiders.exe",
    ]
    for path in vscode_paths:
        if os.path.exists(path):
            subprocess.Popen([path])
            return "Opening VS Code, sir."
    return "VS Code not found. Please install it first."

def open_vscode_folder(folder_name):
    """Open a folder in VS Code"""
    desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
    folder_path = os.path.join(desktop, folder_name)
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    vscode_paths = [
        r"C:\Program Files\Microsoft VS Code\Code.exe",
        r"C:\Users\Lenovo\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    ]
    for path in vscode_paths:
        if os.path.exists(path):
            subprocess.Popen([path, folder_path])
            return f"Opening '{folder_name}' folder in VS Code, sir."
    return "VS Code not found."

def create_file(filename, content=""):
    """Create a new file on Desktop"""
    desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
    filepath = os.path.join(desktop, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Created file: {filename} on Desktop"
    except Exception as e:
        return f"Failed to create file: {e}"

def read_file(filename):
    """Read content of a file"""
    desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
    filepath = os.path.join(desktop, filename)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return f"File content:\n{content[:1000]}"
    except Exception as e:
        return f"Failed to read: {e}"

def run_python_file(filename):
    """Run a Python file and capture output"""
    desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
    filepath = os.path.join(desktop, filename)
    
    try:
        result = subprocess.run(['python', filepath], capture_output=True, text=True, timeout=30)
        if result.stdout:
            return f"Output:\n{result.stdout}"
        elif result.stderr:
            return f"Error:\n{result.stderr}"
        return "File executed (no output)"
    except subprocess.TimeoutExpired:
        return "Execution timed out"
    except Exception as e:
        return f"Failed to run: {e}"