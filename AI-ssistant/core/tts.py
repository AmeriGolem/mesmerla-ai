from __future__ import annotations

import logging
from pathlib import Path

import os
from typing import Any, Literal, Optional

from RealtimeTTS import TextToAudioStream
from sympy import im

FFMPEG_BIN = Path(
    r"C:\Users\aberl\AppData\Local\Microsoft\WinGet\Packages"
    r"\Gyan.FFmpeg.Shared_Microsoft.Winget.Source_8wekyb3d8bbwe"
    r"\ffmpeg-8.1.2-full_build-shared\bin"
)

if not FFMPEG_BIN.is_dir():
    raise FileNotFoundError(
        f"Shared FFmpeg directory not found: {FFMPEG_BIN}"
    )

# Make FFmpeg's DLLs visible to TorchCodec and to the Coqui worker process.
os.environ["PATH"] = f"{FFMPEG_BIN}{os.pathsep}{os.environ.get('PATH', '')}"

if hasattr(os, "add_dll_directory"):
    os.add_dll_directory(str(FFMPEG_BIN))


import logging
import torch
from RealtimeTTS.engines.coqui_engine import CoquiEngine
from RealtimeTTS.engines.pocket_engine import PocketTTSEngine

from core.config import DEFAULT_TTS_LANGUAGE, MODELS_DIR, XTTS_MODEL_NAME

XTTS_VERSION = "v2.0.2"



# RealtimeTTS will store the model in:
# AI-ssistant/models/xtts/v2.0.2/
XTTS_REALTIME_DIR = MODELS_DIR / "xtts"


def _get_tts_device() -> str:
    """Return a device supported by RealtimeTTS's CoquiEngine."""
    if torch.cuda.is_available():
        return "cuda"

    # CoquiEngine currently supports CUDA, MPS and CPU.
    # Intel XPU is therefore left on CPU for now.
    return "cpu"

def load_tts_engine(
    engine_type: Literal["coqui", "pocket"],
    ref_audio_path: str,
    language: str = DEFAULT_TTS_LANGUAGE,
) -> CoquiEngine | PocketTTSEngine:
    """
    Load RealtimeTTS's engine.
    can be either "coqui XTTS or PocketTTS"

    On the first run, XTTS v2.0.2 is downloaded into the project's
    models/xtts/v2.0.2 directory.
    """
    reference_audio = Path(ref_audio_path)

    if not reference_audio.is_file():
        raise FileNotFoundError(
            f"{engine_type} reference audio not found: {reference_audio}"
        )

    XTTS_REALTIME_DIR.mkdir(parents=True, exist_ok=True)

    print(f"🔊 Loading RealtimeTTS {engine_type} on {_get_tts_device()}...")
    print(f"📁 {engine_type} model directory: {XTTS_REALTIME_DIR / XTTS_VERSION}")

    match engine_type.lower():
        case "coqui":
            engine = CoquiEngine(
                model_name=XTTS_MODEL_NAME,
                specific_model=XTTS_VERSION,
                local_models_path=str(XTTS_REALTIME_DIR),
                voice=str(reference_audio),
                language=language,
                device=_get_tts_device(),
                level=logging.ERROR,
                full_sentences=True,
            )
        case "pocket":
            engine = PocketTTSEngine(
                voice=str(reference_audio),
                device=_get_tts_device(),
            )

    print(f"✅ RealtimeTTS {engine_type} engine loaded.")
    return engine

def load_stream(engine: CoquiEngine | PocketTTSEngine, verbose: bool = False) -> TextToAudioStream:
    """
    Load RealtimeTTS's TextToAudioStream for streaming audio output.

    This function is separated from load_tts_engine to allow for
    reloading the TTS engine with a different reference audio file
    without having to reload the entire streaming pipeline.
    """
    stream = TextToAudioStream(engine)
    return stream
