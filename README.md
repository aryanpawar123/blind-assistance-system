🦯 Blind Assistance System (YOLOv10-L)

A real-time AI-powered assistive system that helps visually impaired users navigate safely using computer vision, distance estimation, and voice interaction. The model identifies nearby obstacles, measures their distance, determines direction, and provides hands-free audio instructions.

🚀 Features
🔍 Real-Time Object Detection

Uses YOLOv10-L for high-accuracy detection

GPU-accelerated inference

Detects 80+ object categories

🎤 Voice-Controlled System

Commands supported:

"start detection"

"stop detection"

"calibrate"

🔊 Audio Feedback (Offline TTS)

Announces: object name + distance + direction

Thread-safe speech engine (pyttsx3 + SAPI5)

No internet required

📏 Distance Estimation

Calibration-based distance model

Rolling average smoothing for stability

🖥 Streamlit Dashboard

Start/stop system

View logs

Adjust settings (TTS rate, cooldown, camera index)

🧠 Tech Stack

YOLOv10-L, Ultralytics

PyTorch

OpenCV

SpeechRecognition

PyAudio

pyttsx3

Streamlit

Python 3.11

🏗 System Architecture Diagram

                   ┌──────────────────────────┐
                   │      Laptop Camera        │
                   │   (Live Video Stream)     │
                   └──────────────┬───────────┘
                                  │
                                  ▼
                    ┌────────────────────────┐
                    │      YOLOv10-L Model    │
                    │  (Object Detection +    │
                    │   Bounding Boxes)       │
                    └──────────────┬─────────┘
                                  │
                                  ▼
             ┌────────────────────────────────────────┐
             │   Distance Estimation Module            │
             │  • Pinhole camera model                 │
             │  • Calibration (K-value)                │
             │  • Smoothing (rolling average)          │
             └──────────────┬────────────────────────┘
                             │
                             ▼
                 ┌─────────────────────────┐
                 │ Direction Detection      │
                 │ • Left/Right/Ahead       │
                 │   based on object center │
                 └──────────────┬──────────┘
                                │
                                ▼
               ┌────────────────────────────────┐
               │  TTS Engine (pyttsx3 + SAPI5)  │
               │  • Thread-safe queue worker     │
               │  • Clear offline audio output   │
               └──────────────┬─────────────────┘
                              │
                              ▼
                      ┌───────────────┐
                      │ Audio Output  │
                      │ (Headphones / │
                      │  Speakers)    │
                      └───────────────┘

🎤 Voice Command Control Flow

               ┌─────────────────────────────┐
               │ SpeechRecognition + PyAudio │
               │   (Voice Listener Thread)   │
               └───────────────┬────────────┘
                               │
                               ▼
               ┌──────────────────────────────┐
               │  Voice Commands Detected     │
               │  • "start detection"         │
               │  • "stop detection"          │
               │  • "calibrate"               │
               └───────────────┬─────────────┘
                               │
                               ▼
              ┌──────────────────────────────────┐
              │  System Controller (Main Thread) │
              │  • Start/Stop flags              │
              │  • Trigger calibration           │
              │  • Coordinate modules            │
              └──────────────────────────────────┘




🛠 Installation
git clone https://github.com/aryanpawar123/blind-assistance-system.git
cd blind-assistance-system
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

▶ Run the AI Navigation System
python blind_aid_yolov10_final_voice.py

▶ Run the Streamlit UI
streamlit run app.py

🎤 Voice Commands

start detection

stop detection

calibrate

Press Q to quit the camera window

🧪 Calibration Guide

Say “calibrate”

Place object in front

Press C to capture

Enter real distance in cm

Repeat 3–5 times

Press Q to save calibration

💡 Future Enhancements

Neural depth estimation

Haptic feedback

GPS-based outdoor navigation

Stereo directional audio

🏆 Credits

Developed by Aryan Pawar
Built using YOLOv10 by Ultralytics, OpenCV, PyTorch, and speech technologies.
