"""
blind_aid_yolov10_voice.py
Blind Assistance System using YOLOv10 + Webcam + Voice Activation + Text-To-Speech

Voice Commands:
    "start detection"
    "stop detection"
    "calibrate"

Keyboard:
    Q = Quit program
"""

import cv2
import time
import json
import speech_recognition as sr
from ultralytics import YOLO
import pyttsx3
import threading
import os

# ---------------- CONFIG ----------------
MODEL_WEIGHTS = "yolov10n.pt"
CAM_INDEX = 0
CENTER_ZONE_RATIO = (1/3, 2/3)
CALIB_FILE = "calibration.json"
MIN_SPEAK_DISTANCE_CM = 500

# ---------------- TEXT TO SPEECH (stable version) ----------------

tts_engine = pyttsx3.init('sapi5')
tts_engine.setProperty('rate', 150)
tts_engine.setProperty('volume', 1.0)
voices = tts_engine.getProperty('voices')
tts_engine.setProperty('voice', voices[0].id)

SPEECH_COOLDOWN = 2.0
_last_speech_time = 0

def speak(text):
    """Stable TTS with cooldown + buffer."""
    global _last_speech_time
    now = time.time()
    if now - _last_speech_time < SPEECH_COOLDOWN:
        return

    try:
        print("[SPEAK] ", text)
        tts_engine.say(text)
        tts_engine.runAndWait()
        time.sleep(0.3)  # prevents speech cut-off
        _last_speech_time = time.time()
    except:
        pass


# ---------------- LOAD CALIBRATION ----------------

def load_calibration():
    if os.path.exists(CALIB_FILE):
        with open(CALIB_FILE, "r") as f:
            return json.load(f)
    return {"K": None}

def save_calibration(data):
    with open(CALIB_FILE, "w") as f:
        json.dump(data, f)

calib = load_calibration()


# ---------------- DISTANCE ESTIMATION ----------------

def estimate_distance_cm(h_pixels):
    K = calib.get("K")
    if K is None:
        return int(120000 / (h_pixels + 1))
    return int(K / (h_pixels + 1))


# ---------------- CALIBRATION MODE ----------------

def calibrate_interactive(cap):
    print("\n=== Calibration Mode ===")
    speak("Calibration mode activated")

    K_values = []

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        cv2.putText(frame, "Calibration: Press C to capture, Q to quit",
                    (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
        cv2.imshow("Calibration", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('c'):
            results = model(frame)[0]
            if len(results.boxes) == 0:
                speak("No object detected")
                continue

            h_frame, w_frame = frame.shape[:2]
            centerX = w_frame / 2
            chosen_h = None
            best_area = 0

            for box in results.boxes:
                x1,y1,x2,y2 = map(int, box.xyxy[0])
                cx = (x1+x2)/2
                area = (x2-x1)*(y2-y1)

                if abs(cx-centerX) < w_frame*0.25 and area > best_area:
                    chosen_h = y2-y1
                    best_area = area

            if chosen_h is None:
                speak("Move object to center")
                continue

            print("Captured height:", chosen_h)
            speak("Enter distance in centimeters in the terminal")

            dist = float(input("Real distance (cm): "))
            K_values.append(dist * chosen_h)

        elif key == ord('q'):
            break

    cv2.destroyWindow("Calibration")

    if not K_values:
        speak("Calibration cancelled")
        return

    K_avg = sum(K_values) / len(K_values)
    calib["K"] = K_avg
    save_calibration(calib)

    speak("Calibration completed")
    print("Saved K =", K_avg)


# ---------------- VOICE COMMAND THREAD ----------------

active_detection = False
voice_thread_stop = False

def voice_listener():
    global active_detection, voice_thread_stop

    r = sr.Recognizer()
    mic = sr.Microphone()

    speak("Voice control activated")

    with mic as source:
        r.adjust_for_ambient_noise(source, duration=1)

    while not voice_thread_stop:
        try:
            with mic as source:
                audio = r.listen(source, phrase_time_limit=4)

            cmd = r.recognize_google(audio).lower()
            print("[VOICE]", cmd)

            if "start detection" in cmd:
                active_detection = True
                speak("Detection started")

            elif "stop detection" in cmd:
                active_detection = False
                speak("Detection stopped")

            elif "calibrate" in cmd:
                active_detection = False
                speak("Calibration starting")
                open("DO_CALIBRATE", "w").close()

        except:
            pass


# ---------------- MAIN PROGRAM ----------------

model = YOLO(MODEL_WEIGHTS)

def main():
    global active_detection, voice_thread_stop

    cap = cv2.VideoCapture(CAM_INDEX)
    names = model.names

    # Start voice listener thread
    threading.Thread(target=voice_listener, daemon=True).start()

    speak("System ready")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        h, w = frame.shape[:2]
        left = w * CENTER_ZONE_RATIO[0]
        right = w * CENTER_ZONE_RATIO[1]

        if os.path.exists("DO_CALIBRATE"):
            os.remove("DO_CALIBRATE")
            calibrate_interactive(cap)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

        if not active_detection:
            cv2.putText(frame, "Say 'start detection' to begin",
                        (10,30), cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (0,255,255), 2)
            cv2.imshow("BlindAid", frame)
            continue

        # YOLOv10 detection
        results = model(frame, imgsz=640)[0]
        detections = []

        for box in results.boxes:
            x1,y1,x2,y2 = map(int, box.xyxy[0])
            h_box = y2-y1
            cx = (x1+x2)/2
            cls = int(box.cls[0])
            label = names[cls]

            detections.append({
                "xy": (x1,y1,x2,y2),
                "label": label,
                "h": h_box,
                "cx": cx
            })

        # Find nearest object
        nearest = None
        min_dist = 999999

        for d in detections:
            dist = estimate_distance_cm(d["h"])
            d["dist"] = dist

            if dist < min_dist:
                min_dist = dist
                nearest = d

        # Speak nearest object
        if nearest and nearest["dist"] <= MIN_SPEAK_DISTANCE_CM:
            x_center = nearest["cx"]
            label = nearest["label"]
            dist = nearest["dist"]

            if x_center < left:
                pos = "left"
            elif x_center > right:
                pos = "right"
            else:
                pos = "ahead"

            speak(f"{label} {dist} centimeters {pos}")

        # Draw boxes
        for d in detections:
            x1,y1,x2,y2 = d["xy"]
            cv2.rectangle(frame, (x1,y1),(x2,y2), (0,255,0), 2)
            cv2.putText(frame, f"{d['label']}  {d['dist']}cm",
                        (x1,y1-8), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0,255,0), 2)

        cv2.imshow("BlindAid", frame)

    # Shutdown
    voice_thread_stop = True
    speak("System shutting down")
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
