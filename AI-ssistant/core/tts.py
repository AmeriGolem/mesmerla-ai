from __future__ import annotations

from pathlib import Path
import os
from typing import Optional

from core.config import DEFAULT_TTS_LANGUAGE, XTTS_MODEL_NAME
import gc

try:
    import torch
    from TTS.api import TTS
except Exception:  # pragma: no cover - handled at runtime
    torch = None
    TTS = None

try:
    import winsound
except Exception:  # pragma: no cover - non-Windows fallback
    winsound = None

_xtts = None
_xtts_model_name = XTTS_MODEL_NAME


def clear_memory():
    gc.collect()
    if torch is not None:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        if hasattr(torch, "xpu") and torch.xpu.is_available():
            torch.xpu.empty_cache()

def _get_device() -> str:
    if torch is None:
        return "cpu"
    if torch.cuda.is_available():
        return "cuda"
    if hasattr(torch, "xpu") and torch.xpu.is_available():
        return "xpu"
        pass
    return "cpu"


def load_xtts(model_name: str = XTTS_MODEL_NAME, force_reload: bool = False):
    global _xtts, _xtts_model_name

    if TTS is None:
        raise RuntimeError(
            "Coqui TTS is not installed. Install it with: pip install coqui-tts"
        )

    if _xtts is None or force_reload or _xtts_model_name != model_name:
        print(f"🔊 Loading XTTS model: {model_name}")
        _xtts = TTS(model_name).to(_get_device())
        _xtts_model_name = model_name
    return _xtts



def speak_as_mesmerla(
    text: str,
    ref_audio_path: str,
    ref_text_path: str = "",
    output_path: str = "",
    language: str = DEFAULT_TTS_LANGUAGE,
    speaker: Optional[str] = None,
    voice_dir: Optional[str] = None,
):
    if not text or not text.strip():
        return {"status": "error", "reason": "Empty text."}

    ref_audio = Path(ref_audio_path)
    if not ref_audio.exists():
        return {
            "status": "error",
            "reason": f"Reference audio not found: {ref_audio}",
        }

    out_path = Path(output_path) if output_path else Path("mesmerla_out.wav")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        xtts = load_xtts()
        kwargs = {
            "text": text,
            "file_path": str(out_path),
            "language": language,
        }

        if speaker:
            kwargs["speaker"] = speaker
            if voice_dir:
                kwargs["voice_dir"] = voice_dir

        kwargs["speaker_wav"] = [str(ref_audio)]
        xtts.tts_to_file(**kwargs)
        clear_memory()
        return {"status": "ok", "output_path": str(out_path)}
    except Exception as e:
        clear_memory()
        return {"status": "error", "reason": str(e)}



def play_audio(path: str):
    if winsound is not None:
        winsound.PlaySound(path, winsound.SND_FILENAME)
        return

    if os.name == "posix":
        os.system(f'afplay "{path}" >/dev/null 2>&1 || aplay "{path}" >/dev/null 2>&1')
        return

    raise RuntimeError("No supported audio playback backend found.")
