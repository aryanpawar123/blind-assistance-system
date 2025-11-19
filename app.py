import streamlit as st
import subprocess
import os
import psutil
import time
import json
import signal

st.set_page_config(
    page_title="Blind Assistance System",
    page_icon="🦯",
    layout="wide"
)

# ------------------------------------------------------
# -------------------- UI COMPONENTS -------------------
# ------------------------------------------------------

st.title("🦯 Blind Assistance – YOLOv10 Real-Time Navigation System")

st.markdown("""
This dashboard controls the **Voice-Controlled Blind Assistance System** using YOLOv10.
Use the buttons below to start/stop detection, calibration, and adjust system parameters.
""")

# Session state
if "process" not in st.session_state:
    st.session_state.process = None

if "logs" not in st.session_state:
    st.session_state.logs = []

# ------------------------------------------------------
# ------------------- CONFIG PANEL ----------------------
# ------------------------------------------------------

st.sidebar.header("⚙ System Settings")

tts_rate = st.sidebar.slider("TTS Speed", min_value=100, max_value=200, value=150)
tts_volume = st.sidebar.slider("TTS Volume", min_value=0.1, max_value=1.0, value=1.0)
alert_distance = st.sidebar.slider("Alert Distance (cm)", min_value=50, max_value=1000, value=500)
cooldown_time = st.sidebar.slider("Speech Cooldown (seconds)", min_value=1.0, max_value=5.0, value=2.0)
camera_index = st.sidebar.selectbox("Camera Index", options=[0, 1, 2], index=0)

# Save settings to a JSON file (your YOLO script reads this)
config_data = {
    "tts_rate": tts_rate,
    "tts_volume": tts_volume,
    "alert_distance": alert_distance,
    "cooldown_time": cooldown_time,
    "camera_index": camera_index
}
with open("ui_config.json", "w") as f:
    json.dump(config_data, f)

st.sidebar.success("Settings saved.")

# ------------------------------------------------------
# ----------------- PROCESS MANAGEMENT -----------------
# ------------------------------------------------------

def kill_process_tree(pid):
    try:
        parent = psutil.Process(pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()
    except:
        pass

def start_detection():
    if st.session_state.process is None:
        st.session_state.process = subprocess.Popen(
            ["python", "blind_aid_yolov10.py"],
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        st.session_state.logs.append("🟢 Detection started.")
        st.success("Detection started!")
    else:
        st.warning("System already running.")

def stop_detection():
    if st.session_state.process:
        kill_process_tree(st.session_state.process.pid)
        st.session_state.process = None
        st.session_state.logs.append("🔴 Detection stopped.")
        st.success("Detection stopped.")
    else:
        st.warning("System is not running.")

# ------------------------------------------------------
# ---------------------- MAIN UI ------------------------
# ------------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("▶ Start Detection", use_container_width=True):
        start_detection()

with col2:
    if st.button("⏹ Stop Detection", use_container_width=True):
        stop_detection()

with col3:
    if st.button("📏 Run Calibration", use_container_width=True):
        start_detection()
        st.info("Say 'calibrate' after the window opens.")

# ------------------------------------------------------
# ---------------------- STATUS BOX ---------------------
# ------------------------------------------------------

st.markdown("## 📡 System Status")

if st.session_state.process:
    st.success("🟢 System is RUNNING")
else:
    st.error("🔴 System is STOPPED")

# ------------------------------------------------------
# ---------------------- LOG PANEL ----------------------
# ------------------------------------------------------

st.markdown("## 📜 System Logs")

log_window = st.empty()

# capture live logs from subprocess
if st.session_state.process:
    try:
        output = st.session_state.process.stdout.readline().strip()
        if output:
            st.session_state.logs.append(output)
    except:
        pass

# show last 25 logs
log_window.code("\n".join(st.session_state.logs[-25:]), language="text")

# ------------------------------------------------------
# ---------- OPTIONAL: WEBCAM PREVIEW (LOW FPS) --------
# ------------------------------------------------------

st.markdown("## 🎥 Webcam Preview (optional)")

st.info("""
Streamlit provides **very low FPS webcam streaming**, so your YOLO model 
should continue to run in its own window. This preview is optional.
""")

enable_cam = st.checkbox("Enable Webcam Preview (slow)", value=False)

if enable_cam:
    import cv2

    FRAME_WINDOW = st.image([])

    cam = cv2.VideoCapture(camera_index)

    while enable_cam:
        ret, frame = cam.read()
        if not ret:
            break
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        FRAME_WINDOW.image(frame)
        if not st.checkbox("Enable Webcam Preview (slow)", value=True):
            break

# ------------------------------------------------------
# ---------------------- FOOTER -------------------------
# ------------------------------------------------------

st.markdown("---")
st.markdown("Built for **Blind Navigation Assistance** using YOLOv10 + Voice AI.")

