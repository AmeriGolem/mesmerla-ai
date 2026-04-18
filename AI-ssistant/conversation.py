from core.memory import MesmerlaMemory
from core.speech import record_audio, transcribe_audio
from core.prompt_builder import get_personality
from core.tts import speak_as_mesmerla, play_audio
from core.llm import generate_response
from core.config import MODES, get_paths


def conversation_with_AI(llm, personality: str = "Ayaka", mode: str = "reflective", sil_thresh: int = 5000, verbose: bool = False):
    if verbose:
        print("🎛️ Starting conversation...\n")

    ref_audio_path, ref_text_path, output_path, input_audio_path, _ = get_paths(personality)

    # Record audio
    record_audio(filename=input_audio_path, silence_threshold=sil_thresh)
    if verbose:
        print("🎧 Audio recorded.")

    # Transcribe
    transcript = transcribe_audio(file_path=input_audio_path).strip()
    print(f"📝 You said: {transcript}\n\n")

    # Prompt prep
    template, personality = get_personality(personality)
    memory = MesmerlaMemory(style=personality)
    memory.load(verb=verbose)

    config = MODES.get(mode, MODES["reflective"])
    mode_block = f"[{mode.upper()} MODE]\n{config['description']}"
    memory_block = memory.get_memory_block()

    prompt = template.format(
        mode_block=mode_block,
        memory_block=memory_block,
        user_input=transcript
    )

    # Generate reply
    reply = generate_response(
        llm=llm,
        prompt=prompt,
        max_tokens=config["max_tokens"],
        temperature=config["temperature"],
        top_p=config["top_p"],
        repeat_penalty=config["repeat_penalty"]
    )

    print(reply)

    # Speak output
    response = speak_as_mesmerla(
        text=reply,
        ref_audio_path=ref_audio_path,
        ref_text_path=ref_text_path,
        output_path=output_path
    )

    if response.get("status") == "ok":
        play_audio(response["output_path"])
    else:
        print("⚠️ TTS error:", response)

    # Save memory
    memory.add(transcript, reply)
    memory.save(verbose=verbose)
    return reply

def text_conversation(llm, user_input: str, personality: str = "Mesmerla", mode: str = "reflective", verbose: bool = False):
    if verbose:
        print("💬 Text conversation mode active.\n")
    
    template, personality = get_personality(personality)
    memory = MesmerlaMemory(style=personality)
    memory.load(verb=verbose)

    config = MODES.get(mode, MODES["reflective"])
    mode_block = f"[{mode.upper()} MODE]\n{config['description']}"
    memory_block = memory.get_memory_block()

    prompt = template.format(
        mode_block=mode_block,
        memory_block=memory_block,
        user_input=user_input.strip()
    )

    reply = generate_response(
        llm=llm,
        prompt=prompt,
        max_tokens=config["max_tokens"],
        temperature=config["temperature"],
        top_p=config["top_p"],
        repeat_penalty=config["repeat_penalty"]
    )

    # Save memory
    memory.add(user_input, reply)
    memory.save(verbose=verbose)

    return reply
