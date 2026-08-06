from __future__ import annotations

from collections.abc import Iterator
from typing import Any, cast
import time
import gc

from llama_cpp import Llama

def clear_xpu():
    """Clear PyTorch XPU caches, if PyTorch is using an Intel XPU."""
    gc.collect()
    try:
        import torch
        
        if hasattr(torch, "xpu") and torch.xpu.is_available():
            torch.xpu.synchronize()
            torch.xpu.memory.empty_cache()
    except Exception:
        pass

# Load the default Mesmerla model (Mistral)
def load_model(
    model_path: str, 
    n_ctx: int = 2048, 
    n_threads: int = 12, 
    n_batch: int = 64, 
    verbose: bool = False
) -> Llama:
    print("🧠 Loading model for Mesmerla...")
    start = time.perf_counter()
    
    llm = Llama(
        model_path=model_path,
        n_ctx=n_ctx,
        n_threads=n_threads,
        n_batch=n_batch,
        n_gpu_layers=-1,
        verbose=verbose,
    )
    print(f"✅ Model loaded in {time.perf_counter() - start:.2f}s \nloaded {model_path}")
    return llm


def generate_response_stream(
    llm: Llama,
    system_prompt: str,
    user_prompt:str,
    max_tokens: int = 256,
    temperature: float = 0.7,
    top_p: float = 0.9,
    repeat_penalty: float = 1.1,
    verbose: bool = False,
):
    """Yield the assistant response as soon as each text chunk is generated."""
    start = time.perf_counter()
    first_text_at: float | None = None
    
    
    response = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        repeat_penalty=repeat_penalty,
        stream=True,
    )
    if isinstance(response, dict):
        raise RuntimeError(
            "LLM streaming was requested, but create_chat_completion returned "
            "a completed dictionary instead of a stream."
        )
    try:
        for event in response:
            choices = event.get("choices")
            if not choices:
                continue
            
            text = choices[0].get("delta",{}).get("content")
            if not text:
                continue
            
            if first_text_at is None:
                first_text_at = time.perf_counter()
                if verbose:
                    print(f"⏱️ Time to first text: {first_text_at - start:.2f}s")

            yield text
    finally:
        if verbose:
            print(f"\n ⏱️ Total LLM time: {time.perf_counter() - start:.2f}s")

        # Keep the loaded model and backend caches warm for the next turn.
        # Calling gc.collect() here would add avoidable post-response latency.
        pass
    
def generate_response(
    llm: Llama,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 256,
    temperature: float = 0.7,
    top_p: float = 0.9,
    repeat_penalty: float = 1.1,
    verbose: bool = False,
) -> str:
    """Backward-compatible blocking wrapper around the streaming API."""
    return "".join(
        generate_response_stream(
            llm=llm,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            repeat_penalty=repeat_penalty,
            verbose=verbose,
        )
    ).strip()