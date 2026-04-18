# Configuration: Modes, constants, and paths

MODES = {
    "concise": {
        "description": "Answer in 1 to 2 short sentences only. Prioritize clarity.",
        "max_tokens": 96,
        "temperature": 0.6,
        "top_p": 0.85,
        "repeat_penalty": 1.15
    },
    "reflective": {
        "description": "Answer calmly and thoughtfully. Elaborate freely.",
        "max_tokens": 256,
        "temperature": 0.7,
        "top_p": 0.9,
        "repeat_penalty": 1.1
    },
    "passionate": {
        "description": "You may speak more vividly and emotionally. Express freely.",
        "max_tokens": 320,
        "temperature": 0.8,
        "top_p": 0.95,
        "repeat_penalty": 1.05
    }
}

# Default file paths
def get_paths(personality):
    persona = personality
    if personality == "Mesmerla":
        persona = "Marcus" # set base voice to Marcus
    base_path = "C:\\Users\\aberl\\Desktop\\Projet Code\\Mesmerla_AI\\AI-ssistant"
    ref_audio_path = f"{base_path}\\models\\voices\\{persona}_voice_example.wav"
    ref_text_path = f"{base_path}\\models\\voices\\reference_text_{persona}.txt"
    output_path = f"{base_path}\\output\\mesmerla_out.wav"
    input_audio_path = f"{base_path}\\input\\audio_input.wav"
    model_path = f"{base_path}\\models\\Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf"
    return ref_audio_path, ref_text_path, output_path, input_audio_path, model_path
