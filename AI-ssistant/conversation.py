from __future__ import annotations

from core.memory import MesmerlaMemory
from core.speech import record_audio, transcribe_audio
from core.prompt_builder import get_personality
from core.tts import speak_as_mesmerla, play_audio
from core.llm import generate_response
from core.config import MODES, DEFAULT_TTS_LANGUAGE, get_paths


def conversation_with_AI(
    llm,
    personality: str = "Ayaka",
    mode: str = "reflective",
    sil_thresh: int = 5000,
    verbose: bool = False,
    tts_language: str = DEFAULT_TTS_LANGUAGE,
):
    if verbose:
        print("🎙️ Starting conversation...\n")

    ref_audio_path, ref_text_path, output_path, input_audio_path, _ = get_paths(personality)

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

    reply = generate_response(
        llm=llm,
        system_prompt=system_prompt,
        user_prompt=transcript,
        max_tokens=config["max_tokens"],
        temperature=config["temperature"],
        top_p=config["top_p"],
        repeat_penalty=config["repeat_penalty"],
        verbose=verbose,
    )
    print(reply)

    response = speak_as_mesmerla(
        text=reply,
        ref_audio_path=ref_audio_path,
        ref_text_path=ref_text_path,
        output_path=output_path,
        language=tts_language,
        speaker=personality_name,
    )
    if response.get("status") == "ok":
        play_audio(response["output_path"])
    else:
        print("⚠️ TTS error:", response)

    memory.add(transcript, reply)
    memory.save(verbose=verbose)
    return reply



def text_conversation(
    llm,
    user_input: str,
    personality: str = "Mesmerla",
    mode: str = "reflective",
    verbose: bool = False,
):
    if verbose:
        print("⌨️ Text conversation mode active.\n")

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

    reply = generate_response(
        llm=llm,
        system_prompt=system_prompt,
        user_prompt=user_input.strip(),
        max_tokens=config["max_tokens"],
        temperature=config["temperature"],
        top_p=config["top_p"],
        repeat_penalty=config["repeat_penalty"],
        verbose=verbose,
    )

    memory.add(user_input, reply)
    memory.save(verbose=verbose)
    return reply
