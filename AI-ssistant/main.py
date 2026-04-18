from __future__ import annotations

import os
import time
from pynput import keyboard

from conversation import conversation_with_AI
from core.config import DEFAULT_TTS_LANGUAGE, get_paths
from core.llm import load_model
from core.memory import MesmerlaMemory
from core.tts import load_xtts

# Settings
personality = "Ayaka"
mode = "reflective"
tts_language = DEFAULT_TTS_LANGUAGE

memory = MesmerlaMemory(personality)
memory.reset()

# Load model once
_, _, _, _, model_path = get_paths(personality)
llm = load_model(
    model_path,
    n_ctx=2048,
    n_threads=os.cpu_count(),
    n_batch=64,
    verbose=False,
)

# Preload XTTS once so first reply is not painfully slow.
load_xtts()

continue_conversation = True


def on_key_press(key):
    global continue_conversation
    if hasattr(key, "char") and key.char == "q":
        continue_conversation = False
        print("🛑 Stopping conversation loop... Pressed 'q'")
        return False


print("🔁 Press 'q' at any time to stop.")
listener = keyboard.Listener(on_press=on_key_press)
listener.start()

try:
    while continue_conversation:
        conversation_with_AI(
            llm,
            personality=personality,
            mode=mode,
            verbose=False,
            tts_language=tts_language,
        )
        print("⏳ Listening again...")
        time.sleep(1)
except KeyboardInterrupt:
    print("🛑 Stopping conversation loop... (KeyboardInterrupt)")
    continue_conversation = False
finally:
    listener.join()
    print("👋 Mesmerla session ended.")
