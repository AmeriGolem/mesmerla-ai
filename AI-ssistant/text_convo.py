from core.config import MODES
from core.llm import generate_response
from core.prompt_builder import get_personality
from core.memory import MesmerlaMemory
from llama_cpp import Llama

from core.config import MODES, DEFAULT_TTS_LANGUAGE, get_paths
from core.llm import generate_response_stream

from textwrap import dedent
from html import escape
from IPython.display import HTML, display

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

def text_conversation(
    llm,
    user_input: str,
    personality: str = "Mesmerla",
    mode: str = "reflective",
    jupyter_notebook : bool = False,
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

    if not jupyter_notebook:
        reply = _stream_reply_to_console(
            llm=llm,
            system_prompt=system_prompt,
            user_prompt=user_input.strip(),
            config=config,
            verbose=verbose,
        )
    else:
        reply = _stream_reply_to_notebook(
            llm=llm,
            system_prompt=system_prompt,
            user_prompt=user_input.strip(),
            config=config,
            verbose=verbose,
        )

    memory.add(user_input, reply)
    memory.save(verbose=verbose)
    return reply

def _stream_reply_to_notebook(
    llm,
    system_prompt: str,
    user_prompt: str,
    config,
    verbose: bool = False,
) -> str:
    parts: list[str] = []

    output = display(
        HTML(
            """
            <div style="
                white-space: pre-wrap;
                overflow-wrap: anywhere;
                word-break: normal;
                max-width: 100%;
            ">
                <strong>💬 Mesmerla:</strong>
                <span id="mesmerla-stream"></span>
            </div>
            """
        ),
        display_id=True,
    )

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
        reply_so_far = escape("".join(parts))

        html = dedent(f"""
        <div style="
            white-space: pre-wrap;
            overflow-wrap: anywhere;
            word-break: normal;
            max-width: 100%;
        ">
        <strong>💬 Mesmerla:</strong> <span>{reply_so_far}</span>
        </div>
        """).strip()
        output.update(HTML(html))

    return "".join(parts).strip()