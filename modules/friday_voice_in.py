import json
import queue
import threading
import time
import sounddevice as sd
import vosk
import os
import numpy as np

WAKE_WORDS = ["hey friday", "hi friday", "okay friday", "hey, friday", "hey friday"]

class FridayVoiceIn:
    def __init__(self):
        model_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'models', 'vosk', 'vosk-model-small-en-in-0.4'
        )
        if not os.path.exists(model_path):
            print(f"[VoiceIn] ⚠  Model not found: {model_path}")
            self.model = None
        else:
            self.model = vosk.Model(model_path)
            print("[VoiceIn] ✓  Vosk model loaded")

        self.sample_rate = 16000
        self.always_awake = False
        self._browser_opened = False

        self._audio_q = queue.Queue()
        self._command_event = threading.Event()
        self._command_text = ""

        self._awake = False
        self._running = False
        self._muted = False
        self._reset_flag = False

        self.on_status = None
        self.on_transcript = None
        self.on_wake_response = None

        self.min_command_length = 3
        self.silence_timeout = 1.5
        
        # Clap detection variables
        self.clap_count = 0
        self.last_clap_time = 0

    def start(self):
        if self._running or not self.model:
            return
        self._running = True
        t = threading.Thread(target=self._recognition_loop, daemon=True)
        t.start()
        print("[VoiceIn] 🎙  Mic is OPEN — always listening. Say 'Hey Friday' or clap twice")

    def stop(self):
        self._running = False

    def ready_for_next(self):
        while not self._audio_q.empty():
            try:
                self._audio_q.get_nowait()
            except:
                break
        
        self._command_event.clear()
        self._command_text = ""
        self._muted = False
        self._reset_flag = True
        
        if self.always_awake:
            self._awake = True
            self._emit_status("listening")
        else:
            self._awake = False
            self._emit_status("wake")
        
        print(f"[VoiceIn] ✓ Ready (always_awake={self.always_awake})")

    def _detect_clap(self, indata):
        """Detect clap from audio data"""
        audio = np.frombuffer(indata, dtype=np.int16).astype(np.float32)
        volume = np.sqrt(np.mean(audio**2))
        
        if volume > 5000:  # Threshold for clap
            current_time = time.time()
            if current_time - self.last_clap_time < 0.5:  # Within 0.5 seconds
                self.clap_count += 1
            else:
                self.clap_count = 1
            self.last_clap_time = current_time
            
            if self.clap_count >= 2:  # Two claps detected
                print("[VoiceIn] 👏 Clap detected! Waking up...")
                self.clap_count = 0
                return True
        return False

    def _recognition_loop(self):
        rec = vosk.KaldiRecognizer(self.model, self.sample_rate)

        with sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=4000,
            dtype='int16',
            channels=1,
            callback=self._mic_cb
        ):
            print("[VoiceIn] 🟢 Mic stream open. Waiting for wake word or clap...")
            self._emit_status("wake")

            while self._running:
                if self._reset_flag:
                    rec = vosk.KaldiRecognizer(self.model, self.sample_rate)
                    self._reset_flag = False
                    time.sleep(0.1)
                    print("[VoiceIn] 🔄 Vosk recognizer reset")
                    continue

                try:
                    data = self._audio_q.get(timeout=0.5)
                except queue.Empty:
                    continue

                if self._muted:
                    continue

                # Check for clap first
                if self._detect_clap(data):
                    self._awake = True
                    self.always_awake = True
                    if callable(self.on_wake_response):
                        self.on_wake_response()
                    self._emit_status("listening")
                    self._emit_transcript("Clap detected!", is_command=False)
                    # Clear queue and reset
                    rec = vosk.KaldiRecognizer(self.model, self.sample_rate)
                    while not self._audio_q.empty():
                        try:
                            self._audio_q.get_nowait()
                        except:
                            break
                    continue

                is_final = rec.AcceptWaveform(data)
                text = ""

                if is_final:
                    result = json.loads(rec.Result())
                    text = result.get("text", "").strip().lower()
                else:
                    partial = json.loads(rec.PartialResult())
                    text = partial.get("partial", "").strip().lower()

                if not text:
                    continue

                # Don't process very short partials
                if len(text) < 2:
                    continue

                # MODE 1: SLEEPING — scan for wake phrase
                if not self._awake:
                    if any(w in text for w in WAKE_WORDS):
                        print(f"[VoiceIn] 🔔 Wake word! heard: '{text}'")
                        self._awake = True
                        self.always_awake = True
                        
                        if callable(self.on_wake_response):
                            self.on_wake_response()
                        
                        rec = vosk.KaldiRecognizer(self.model, self.sample_rate)
                        while not self._audio_q.empty():
                            try:
                                self._audio_q.get_nowait()
                            except:
                                break
                        
                        self._emit_status("listening")
                        self._emit_transcript("Hey Friday!", is_command=False)
                    continue

                # MODE 2: AWAKE — capture the command
                if is_final:
                    clean = text
                    for w in WAKE_WORDS:
                        clean = clean.replace(w, "").strip()
                    
                    meaningless = ["uh", "um", "ah", "huh", "eh", "oh", "mm", "hmm", "like", "so", "and", "the"]
                    
                    if clean and len(clean) >= self.min_command_length and clean not in meaningless:
                        print(f"[VoiceIn] 📝 Command captured: '{clean}'")
                        self._command_text = clean
                        self._awake = False
                        
                        rec = vosk.KaldiRecognizer(self.model, self.sample_rate)
                        while not self._audio_q.empty():
                            try:
                                self._audio_q.get_nowait()
                            except:
                                break
                        
                        self._emit_transcript(clean, is_command=True)
                        self._emit_status("thinking")
                        self._command_event.set()
                    elif clean and clean in meaningless:
                        print(f"[VoiceIn] 🔇 Ignored meaningless utterance: '{clean}'")

    def _mic_cb(self, indata, frames, time_info, status):
        if status:
            print(f"[VoiceIn] mic: {status}")
        self._audio_q.put(bytes(indata))

    def listen(self, timeout=30):
        self._command_event.clear()
        fired = self._command_event.wait(timeout=timeout)
        
        if fired:
            cmd = self._command_text
            self._command_text = ""
            return cmd
        
        if not self.always_awake:
            self._awake = False
            self._emit_status("wake")
        else:
            self._awake = True
            self._emit_status("listening")
        
        return ""

    def _emit_status(self, status):
        if callable(self.on_status):
            try:
                self.on_status(status)
            except Exception as e:
                print(f"[VoiceIn] on_status error: {e}")

    def _emit_transcript(self, text, is_command=False):
        if callable(self.on_transcript):
            try:
                self.on_transcript(text, is_command)
            except Exception as e:
                print(f"[VoiceIn] on_transcript error: {e}")