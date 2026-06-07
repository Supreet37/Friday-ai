import ollama
import pythoncom
import win32com.client
import time

def open_word_and_write(content):
    """Open Microsoft Word and write content"""
    try:
        # Initialize COM
        pythoncom.CoInitialize()
        
        # Open Word
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = True
        
        # Create new document
        doc = word.Documents.Add()
        
        # Write content
        doc.Content.Text = content
        
        return True, "Document created in Word"
    except Exception as e:
        return False, f"Word error: {e}"

def write_to_word(prompt):
    """Generate content using Ollama and write to Word"""
    try:
        # Ask Ollama to write content
        full_prompt = f"""Write only the content for this request. No explanations. Just the text.

Request: {prompt}"""

        response = ollama.chat(model="qwen2.5:1.5b", messages=[{"role": "user", "content": full_prompt}])
        content = response["message"]["content"]
        
        # Open Word and write
        success, message = open_word_and_write(content)
        
        if success:
            return f"📄 Document opened in Microsoft Word: {prompt[:50]}..."
        else:
            return f"❌ {message}"
            
    except Exception as e:
        return f"❌ Failed: {e}"

def write_from_text(user_input):
    """Parse user input and write to Word"""
    # Remove trigger words
    prompt = user_input
    for word in ["write", "in word", "word", "open word", "create"]:
        prompt = prompt.replace(word, "")
    prompt = prompt.strip()
    
    if not prompt:
        return "What should I write? Example: 'write apology letter for missing meeting'"
    
    return write_to_word(prompt)