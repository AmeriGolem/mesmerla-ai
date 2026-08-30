from __future__ import annotations

from pathlib import Path

# Configuration: Modes, constants, and paths
MODES = {
    "concise": {
        "description": "Answer in 1 to 2 short sentences only. Prioritize clarity.",
        "max_tokens": 96,
        "temperature": 0.6,
        "top_p": 0.85,
        "repeat_penalty": 1.15,
    },
    "reflective": {
        "description": "Answer calmly and thoughtfully. Elaborate freely.",
        "max_tokens": 256,
        "temperature": 0.7,
        "top_p": 0.9,
        "repeat_penalty": 1.1,
    },
    "passionate": {
        "description": "Answer with more vivid emotion while staying natural.",
        "max_tokens": 320,
        "temperature": 0.8,
        "top_p": 0.95,
        "repeat_penalty": 1.05,
    },
}

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
VOICES_DIR = MODELS_DIR / "voices"
OUTPUT_DIR = BASE_DIR / "output"
INPUT_DIR = BASE_DIR / "input"
MEMORY_DIR = BASE_DIR / "memory_logs"

#LLM_MODEL_PATH = MODELS_DIR / "Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf"
LLM_MODEL_PATH = MODELS_DIR / "Meta-Llama-3-8B-Instruct-Q4_K_M.gguf"
XTTS_MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"
DEFAULT_TTS_LANGUAGE = "en"

PERSONA_VOICE_MAP = {
    "Mesmerla": "Marcus",
    "Ayaka": "Ayaka",
    "Zhongli": "Zhongli",
    "HuTao": "HuTao",
    "Marcus": "Marcus",
}


def ensure_runtime_dirs() -> None:
    for path in (OUTPUT_DIR, INPUT_DIR, MEMORY_DIR):
        path.mkdir(parents=True, exist_ok=True)


def get_paths(personality: str, combined_audio:bool = False):
    """Return the same tuple shape as the legacy code for compatibility."""
    ensure_runtime_dirs()
    persona = PERSONA_VOICE_MAP.get(personality, personality)
    ref_audio_path = VOICES_DIR / f"{persona}_voice_example.wav"
    if combined_audio:
        ref_audio_path = VOICES_DIR / "combined.wav"
    ref_text_path = VOICES_DIR / f"reference_text_{persona}.txt"
    output_path = OUTPUT_DIR / "mesmerla_out.wav"
    input_audio_path = INPUT_DIR / "audio_input.wav"
    model_path = LLM_MODEL_PATH
    return (
        str(ref_audio_path),
        str(ref_text_path),
        str(output_path),
        str(input_audio_path),
        str(model_path),
    )
