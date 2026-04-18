from core.config import MODES
from core.llm import generate_response
from core.prompt_builder import get_personality
from core.memory import MesmerlaMemory

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

    return reply, prompt