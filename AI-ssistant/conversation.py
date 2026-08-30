from __future__ import annotations

from llama_cpp import Llama

from core.config import MODES, DEFAULT_TTS_LANGUAGE, get_paths
from core.llm import generate_response_stream
from core.memory import MesmerlaMemory
from core.speech import record_audio, transcribe_audio
from core.prompt_builder import get_personality

from RealtimeTTS import TextToAudioStream
from RealtimeTTS.engines.coqui_engine import CoquiEngine

def _stream_reply_to_console(
    llm: Llama,
    system_prompt: str,
    user_prompt: str,
    config: dict,
    verbose: bool,
) -> str:
    """Print generated text immediately while also collecting the final reply."""
    
    parts: list[str] = []
    
    print("💬 Mesmerla: ", end="", flush=True)
    
    for chunk in generate_response_stream(
        llm=llm,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_tokens=config["max_tokens"],
        temperature=config["temperature"],
        top_p=config["top_p"],
        repeat_penalty=config["repeat_penalty"],
        verbose=verbose,
    ):
        parts.append(chunk)
        print(chunk, end="", flush=True)
    print()
    
    return "".join(parts).strip()


def _stream_reply_to_audio_and_console(
    llm:Llama,
    coqui_engine: CoquiEngine,
    system_prompt: str,
    user_prompt: str,
    config: dict,
    verbose: bool,
    tts_language: str = DEFAULT_TTS_LANGUAGE,
) -> str:
    """Print generated text immediately while also collecting the final reply."""
    
    parts: list[str] = []
    
    print("💬 Mesmerla: ", end="", flush=True)
    
    llm_stream = generate_response_stream(
        llm=llm,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_tokens=config["max_tokens"],
        temperature=config["temperature"],
        top_p=config["top_p"],
        repeat_penalty=config["repeat_penalty"],
        verbose=verbose,
    )

    def displayed_stream():
        for chunk in llm_stream:
            parts.append(chunk)
            print(chunk, end="", flush=True)
            yield chunk

    tts_stream = TextToAudioStream(coqui_engine, language=tts_language)

    tts_stream.feed(displayed_stream())
    
    tts_stream.play()
    print()
    
    return "".join(parts).strip()

def conversation_with_AI(
    llm,
    coqui_engine: CoquiEngine,
    personality: str = "Ayaka",
    mode: str = "reflective",
    sil_thresh: int = 5000,
    verbose: bool = False,
    tts_language: str = DEFAULT_TTS_LANGUAGE,
) -> str:
    if verbose:
        print("🎙️ Starting conversation...\n")

    _, _, _, input_audio_path, _ = get_paths(personality)

    record_audio(filename=input_audio_path, silence_threshold=sil_thresh)
    if verbose:
        print("✅ Audio recorded.")

    transcript = transcribe_audio(file_path=input_audio_path).strip()
    if not transcript:
        print("⚠️ No speech detected.")
        return ""

    print(f"🗣️ You said: {transcript}\n")

    template, personality_name = get_personality(personality)
    memory = MesmerlaMemory(style=personality_name)
    memory.load(verb=verbose)

    config = MODES.get(mode, MODES["reflective"])
    mode_block = f"[{mode.upper()} MODE]\n{config['description']}"
    memory_block = memory.get_memory_block()
    system_prompt = template.format(
        mode_block=mode_block,
        memory_block=memory_block
    )

    reply = _stream_reply_to_audio_and_console(
        llm=llm,
        coqui_engine=coqui_engine,
        system_prompt=system_prompt,
        user_prompt=transcript,
        config=config,
        verbose=verbose,
        tts_language=tts_language,
    )

    memory.add(transcript, reply)
    memory.save(verbose=verbose)
    return reply



def text_conversation(
    llm,
    user_input: str,
    personality: str = "Mesmerla",
    mode: str = "reflective",
    verbose: bool = False,
) -> str:
    
    if verbose:
        print("⌨️ Text conversation mode active.\n")

    cleaned_input = user_input.strip()
    if not cleaned_input:
        return ""
    
    template, personality_name = get_personality(personality)
    memory = MesmerlaMemory(style=personality_name)
    memory.load(verb=verbose)

    config = MODES.get(mode, MODES["reflective"])
    mode_block = f"[{mode.upper()} MODE]\n{config['description']}"
    memory_block = memory.get_memory_block()
    system_prompt = template.format(
        mode_block=mode_block,
        memory_block=memory_block
    )

    reply = _stream_reply_to_console(
        llm=llm,
        system_prompt=system_prompt,
        user_prompt=user_input.strip(),
        config=config,
        verbose=verbose,
    )

    memory.add(user_input, reply)
    memory.save(verbose=verbose)
    return reply

