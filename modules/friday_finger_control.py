import cv2
import mediapipe as mp
import pyautogui
import threading
import time

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

class FingerControl:
    def __init__(self):
        self.is_running = False
        self.cap = None
        self.callback = None
    
    def count_fingers(self, landmarks, side):
        fingers = []
        if side == "Right":
            fingers.append(1 if landmarks[4].x > landmarks[3].x else 0)
        else:
            fingers.append(1 if landmarks[4].x < landmarks[3].x else 0)
        for tip in [8, 12, 16, 20]:
            fingers.append(1 if landmarks[tip].y < landmarks[tip-2].y else 0)
        return fingers
    
    def set_callback(self, callback):
        self.callback = callback
    
    def start(self):
        self.is_running = True
        self.cap = cv2.VideoCapture(0)
        threading.Thread(target=self._process, daemon=True).start()
        return "Finger control started"
    
    def stop(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        return "Finger control stopped"
    
    def _process(self):
        screen_w, screen_h = pyautogui.size()
        while self.is_running:
            ret, frame = self.cap.read()
            if not ret:
                continue
            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(frame_rgb)
            if results.multi_hand_landmarks:
                for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                    side = handedness.classification[0].label
                    fingers = self.count_fingers(hand_landmarks.landmark, side)
                    total = sum(fingers)
                    index_tip = hand_landmarks.landmark[8]
                    x = int(index_tip.x * screen_w)
                    y = int(index_tip.y * screen_h)
                    action = None
                    if total == 1 and fingers[1] == 1:
                        action = "move"
                        pyautogui.moveTo(x, y)
                    elif total == 2 and fingers[1] == 1 and fingers[2] == 1:
                        action = "click"
                        pyautogui.click()
                    elif fingers[0] == 1 and total == 1:
                        action = "scroll_up"
                        pyautogui.scroll(300)
                    elif fingers[4] == 1 and total == 1:
                        action = "scroll_down"
                        pyautogui.scroll(-300)
                    if action and self.callback:
                        self.callback(action, x, y)
            cv2.imshow("Friday Finger Control", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.stop()
                break
        cv2.destroyAllWindows()

finger_control = FingerControl()