import subprocess
import os
import tempfile
import pygame
import threading
stop_speaking_flag = False

class FridayVoiceOut:
    def __init__(self):
        base = os.path.dirname(os.path.dirname(__file__))
        self.piper_path    = os.path.join(base, 'models', 'tts', 'piper', 'piper.exe')
        self.english_voice = os.path.join(base, 'models', 'tts', 'piper', 'en_US-lessac-medium.onnx')
        self.hindi_model   = os.path.join(base, 'models', 'tts', 'mms-hindi-female')
        self.current_language = "en"

        # Bug 1 fix: init with explicit sample rate + mono channel
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=1, buffer=512)
        pygame.mixer.init()
        print("[VoiceOut] pygame mixer ready")

        # Bug 4 check: warn early if files are missing
        self._check_piper_files()

    def _check_piper_files(self):
        for path in [self.piper_path, self.english_voice, self.english_voice + '.json']:
            if not os.path.exists(path):
                print(f"[VoiceOut] ⚠ Missing file: {path}")
            else:
                print(f"[VoiceOut] ✓ Found: {path}")

    def _play_wav(self, path):
        global stop_speaking_flag
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            return
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.wait(50)
                if stop_speaking_flag:
                    pygame.mixer.music.stop()
                    stop_speaking_flag = False
                    break
        except:
            pass
        finally:
            try:
                os.unlink(path)
            except:
                pass

    def _speak_piper(self, text, model_path):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        tmp.close()

        cmd = [self.piper_path, '--model', model_path, '--output_file', tmp.name]

        try:
            # Bug 2 & 3 fix: check return code and stderr
            proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate(input=text.encode('utf-8'), timeout=15)

            if proc.returncode != 0:
                print(f"[VoiceOut] ⚠ Piper failed (code {proc.returncode}): {stderr.decode()}")
                return

            if stderr:
                print(f"[VoiceOut] Piper stderr: {stderr.decode()}")

            self._play_wav(tmp.name)

        except subprocess.TimeoutExpired:
            proc.kill()
            print("[VoiceOut] ⚠ Piper timed out")
        except FileNotFoundError:
            print(f"[VoiceOut] ⚠ piper.exe not found at: {self.piper_path}")

    def _speak_mms(self, text):
        try:
            from transformers import pipeline
            import scipy.io.wavfile as wav
            import numpy as np

            tts = pipeline("text-to-speech", model=self.hindi_model)
            result = tts(text)
            audio = np.array(result["audio"]).squeeze()
            rate  = result["sampling_rate"]

            tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            wav.write(tmp.name, rate, (audio * 32767).astype(np.int16))
            tmp.close()
            self._play_wav(tmp.name)
        except Exception as e:
            print(f"[VoiceOut] Hindi TTS error: {e}")

    def speak(self, text, language="en"):
        if not text or not text.strip():
            return
        self.current_language = language
        print(f"[VoiceOut] Speaking ({language}): {text[:60]}...")

        if language == "hi":
            self._speak_mms(text)
        else:
            self._speak_piper(text, self.english_voice)


    def stop_speaking(self):
        global stop_speaking_flag
        stop_speaking_flag = True
        pygame.mixer.music.stop()
        return "Stopped speaking,Sup"