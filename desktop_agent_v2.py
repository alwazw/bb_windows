import os
import time
import json
import random
import mss
import streamlit as st
from io import BytesIO
from PIL import Image
from google import genai
from google.genai import types

# --- CONFIGURATION & PATHS ---
CONFIG_FILE = "agent_config.json"

# --- HELPER FUNCTIONS ---
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(key):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"api_key": key}, f)

# --- 1. THE STEALTH MOUSE DRIVER ---
class HumanMouse:
    def __init__(self):
        import pyautogui
        pyautogui.FAILSAFE = True
        self.pyautogui = pyautogui
        self.screen_width, self.screen_height = self.pyautogui.size()

    def _get_point_on_curve(self, points, t):
        if len(points) == 1: return points[0]
        new_points = []
        for i in range(len(points) - 1):
            x = (1 - t) * points[i][0] + t * points[i+1][0]
            y = (1 - t) * points[i][1] + t * points[i+1][1]
            new_points.append((x, y))
        return self._get_point_on_curve(new_points, t)

    def move_to(self, target_x, target_y, duration=0.5):
        start_x, start_y = self.pyautogui.position()
        duration += random.uniform(-0.1, 0.3)
        if duration < 0.3: duration = 0.3

        control_1 = (start_x + random.randint(-300, 300), start_y + random.randint(-300, 300))
        control_2 = (target_x + random.randint(-300, 300), target_y + random.randint(-300, 300))
        points = [(start_x, start_y), control_1, control_2, (target_x, target_y)]

        start_time = time.time()
        while time.time() - start_time < duration:
            t = (time.time() - start_time) / duration
            x, y = self._get_point_on_curve(points, t)
            safe_x = max(0, min(self.screen_width-1, x + random.randint(-2, 2)))
            safe_y = max(0, min(self.screen_height-1, y + random.randint(-2, 2)))
            self.pyautogui.moveTo(safe_x, safe_y)
            time.sleep(random.uniform(0.001, 0.01))
        self.pyautogui.moveTo(target_x, target_y)

    def click(self):
        time.sleep(random.uniform(0.1, 0.3))
        self.pyautogui.click()

    def type(self, text_to_type):
        for char in text_to_type:
            self.pyautogui.write(char)
            time.sleep(random.uniform(0.05, 0.15))

# --- 2. THE VISION AGENT ---
class VisionAgent:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.mouse = HumanMouse()
        self.sct = mss.mss()

    def capture_screen(self):
        monitor = self.sct.monitors[1]
        sct_img = self.sct.grab(monitor)
        return Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

    def analyze_and_act(self, instruction, history_context):
        screenshot = self.capture_screen()
        width, height = screenshot.size

        buffered = BytesIO()
        screenshot.save(buffered, format="JPEG", quality=80)
        img_bytes = buffered.getvalue()

        system_prompt = f"""
        You are a Human-Computer Interaction agent controlling a {width}x{height} Windows desktop.
        RETURN JSON ONLY.
        Format: {{ "reasoning": "str", "action": "CLICK"|"TYPE"|"SCROLL"|"DONE", "coordinates": [x, y], "text": "str", "scroll_amount": int }}
        """

        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=[
                    types.Content(role="user", parts=[
                        types.Part.from_text(system_prompt),
                        types.Part.from_text(f"Task: {instruction}\nHistory: {history_context}"),
                        types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")
                    ])
                ],
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            return json.loads(response.text)
        except Exception as e:
            return {"action": "WAIT", "reasoning": f"Error: {str(e)}"}

# --- 3. THE UI (STREAMLIT) ---
def main():
    st.set_page_config(layout="wide", page_title="Gemini Desktop Controller")
    st.title("🤖 Gemini Desktop Controller")

    # --- API KEY MANAGEMENT ---
    config = load_config()

    if "api_key_valid" not in st.session_state:
        st.session_state.api_key_valid = False

    if not st.session_state.api_key_valid:
        with st.container():
            st.info("🔐 Please enter your Google Gemini API Key to start.")

            # Pre-fill if found in config
            default_key = config.get("api_key", "")
            user_key = st.text_input("API Key", value=default_key, type="password")

            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("Start Agent"):
                    if user_key.startswith("AI"):
                        save_config(user_key)
                        st.session_state.agent = VisionAgent(user_key)
                        st.session_state.api_key_valid = True
                        st.session_state.logs = []
                        st.rerun()
                    else:
                        st.error("Invalid API Key format.")
            with col2:
                if st.button("Clear Saved Key"):
                    if os.path.exists(CONFIG_FILE): os.remove(CONFIG_FILE)
                    st.rerun()
        return

    # --- MAIN INTERFACE (Only shows if Key is valid) ---
    with st.sidebar:
        if st.button("🔄 Change API Key"):
            st.session_state.api_key_valid = False
            st.rerun()
        st.divider()
        loop_count = st.number_input("Actions per command", 1, 50, 5)

    user_input = st.chat_input("Ex: 'Go to Facebook listings and delete sold items'")

    if user_input:
        st.session_state.logs.append(f"User: {user_input}")
        status = st.empty()

        for i in range(loop_count):
            status.info(f"Step {i+1}: Analyzing screen...")

            # Analyze
            decision = st.session_state.agent.analyze_and_act(user_input, str(st.session_state.logs[-2:]))
            st.session_state.logs.append(f"🤖 {decision.get('action')}: {decision.get('reasoning')}")

            # Execute
            action = decision.get("action")
            if action == "CLICK":
                c = decision.get("coordinates")
                if c:
                    st.session_state.agent.mouse.move_to(c[0], c[1])
                    st.session_state.agent.mouse.click()
            elif action == "TYPE":
                text_to_type = decision.get("text", "")
                if text_to_type:
                    st.session_state.agent.mouse.type(text_to_type)
            elif action == "DONE":
                break

            # Show logs
            with st.container():
                for log in st.session_state.logs[-3:]:
                    st.text(log)

            time.sleep(2)
        status.success("Done!")

if __name__ == "__main__":
    main()
