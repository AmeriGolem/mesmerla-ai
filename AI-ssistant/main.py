import time
from pynput import keyboard
from core.config import get_paths
from core.llm import load_model
from conversation import conversation_with_AI
from core.tts import _server_process
from core.memory import MesmerlaMemory
import os

# Settings
personality = "Ayaka"
mode = "reflective"

memory = MesmerlaMemory(personality)
memory.reset()


# Load model once
_, _, _, _, model_path = get_paths(personality)
llm = load_model(model_path,
                n_ctx=2048,
                n_threads=os.cpu_count(),  # full CPU usage (you have 18 cores!)
                n_batch=64,                # larger batch = faster, up to 128 if stable
                verbose=False
                )

# Global control
continue_conversation = True

# Define keypress handling
def on_key_press(key):
    global continue_conversation
    if hasattr(key, 'char') and key.char == 'q':
        continue_conversation = False
        print("🛑 Stopping conversation loop... Pressed 'q'")
        return False  # Stops listener

print("🔁 Press 'q' at any time to stop.")
listener = keyboard.Listener(on_press=on_key_press)
listener.start()

try:
    while continue_conversation:
        conversation_with_AI(llm, personality=personality, mode=mode, verbose=False)
        print("⏳ Listening again...")
        time.sleep(1)
except KeyboardInterrupt:
    print("🛑 Stopping conversation loop... (KeyboardInterrupt)")
    continue_conversation = False

listener.join()

# Gracefully shut down server if it's still running
if _server_process and _server_process.poll() is None:
    _server_process.terminate()
    print("🔌 Mesmerla TTS server terminated.")

print("👋 Mesmerla session ended.")
