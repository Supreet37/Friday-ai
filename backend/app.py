from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import sys, os, threading, queue, json, webbrowser, time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.friday_brain import FridayBrain
from modules.friday_voice_out import FridayVoiceOut
from modules.friday_voice_in import FridayVoiceIn

app = Flask(__name__, static_folder='../ui/web', static_url_path='')
CORS(app)

brain = FridayBrain()
voice = FridayVoiceOut()
listener = FridayVoiceIn()

# SSE clients
_sse_clients = []
_sse_lock = threading.Lock()
_current_status = "wake"
_browser_opened = False

def broadcast(event: str, data: dict):
    payload = f"event: {event}\ndata: {json.dumps(data)}\n\n"
    with _sse_lock:
        dead = []
        for q in _sse_clients:
            try:
                q.put_nowait(payload)
            except queue.Full:
                dead.append(q)
        for q in dead:
            _sse_clients.remove(q)

# Listener callbacks
def _on_status(status):
    global _browser_opened, _current_status
    _current_status = status
    broadcast("status", {"status": status})
    
    # Open browser only once, when first time listening
    if status == "listening" and not _browser_opened:
        _browser_opened = True
        # Only open browser once, and only if not already open
        import webbrowser
        webbrowser.open("http://127.0.0.1:5000")
        print("[Friday] Browser opened once")

def _on_transcript(text, is_command):
    broadcast("transcript", {"text": text, "is_command": is_command})

def _on_wake_response():
    # Play immediate "Hi" when wake word detected
    voice.speak("Hi", "en")

listener.on_status = _on_status
listener.on_transcript = _on_transcript
listener.on_wake_response = _on_wake_response

# Voice pipeline
def voice_pipeline():
    print("[Friday] 🎙  Voice pipeline running. Say 'Hey Friday' anytime.")
    
    while True:
        text = listener.listen(timeout=30)
        
        if not text or not text.strip():
            continue
        
        # Think
        broadcast("status", {"status": "thinking"})
        response_text = ""
        try:
            response_text = brain.chat(text)
        except Exception as e:
            print(f"[Friday] Brain error: {e}")
            response_text = "Sorry yaar, kuch gadbad ho gayi. Please try again."
        
        if not response_text.strip():
            listener.ready_for_next()
            continue
        
        # Send to UI
        broadcast("message", {
            "user": text,
            "response": response_text,
            "language": brain.detected_language
        })
        
        # Speak
        broadcast("status", {"status": "speaking"})
        listener._muted = True
        try:
            voice.speak(response_text, brain.detected_language)
        finally:
            listener.ready_for_next()

# Start
listener.start()
threading.Thread(target=voice_pipeline, daemon=True).start()

# Routes
@app.route('/')
def index():
    return send_from_directory('../ui/web', 'index.html')

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    assets_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'ui', 'assests'
    )
    return send_from_directory(assets_path, filename)

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('../ui/web', path)

@app.route('/api/stream')
def stream():
    client_q = queue.Queue(maxsize=60)
    with _sse_lock:
        _sse_clients.append(client_q)
    
    # Send current status to new client
    client_q.put(f"event: status\ndata: {json.dumps({'status': _current_status})}\n\n")
    
    def generate():
        try:
            while True:
                try:
                    yield client_q.get(timeout=20)
                except queue.Empty:
                    yield ": heartbeat\n\n"
        except GeneratorExit:
            with _sse_lock:
                try:
                    _sse_clients.remove(client_q)
                except ValueError:
                    pass
    
    return Response(generate(), mimetype='text/event-stream',
                    headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    response_text = brain.chat(user_message)
    threading.Thread(target=voice.speak, args=(response_text, brain.detected_language), daemon=True).start()
    return jsonify({'response': response_text, 'language': brain.detected_language})

@app.route('/api/clear', methods=['POST'])
def clear():
    brain.clear_history()
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    print("=" * 55)
    print("  FRIDAY is starting up...")
    print("  Mic is OPEN. Say 'Hey Friday' to begin.")
    print("  Browser will open automatically on first wake.")
    print("  After that, just keep talking — no need to say 'Hey Friday' again!")
    print("  Press Ctrl+C to shut everything down.")
    print("=" * 55)
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

@app.route('/api/launch_finger_control', methods=['POST'])
def launch_finger_control():
    import subprocess
    import os
    import sys
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        script_path = os.path.join(root_dir, 'finger_control.py')
        
        if os.path.exists(script_path):
            # Open in new window
            subprocess.Popen(['python', script_path], creationflags=subprocess.CREATE_NEW_CONSOLE)
            return jsonify({'status': 'success', 'message': 'Finger control launched'})
        else:
            return jsonify({'status': 'error', 'message': f'File not found at {script_path}'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})