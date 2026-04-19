from llama_cpp import Llama
import time
import gc

def clear_xpu():
    gc.collect()
    try:
        import torch
        if hasattr(torch, "xpu") and torch.xpu.is_available():
            torch.xpu.synchronize()
            torch.xpu.memory.empty_cache()
    except Exception:
        pass

# Load the default Mesmerla model (Mistral)
def load_model(model_path, n_ctx=2048, n_threads=12, n_batch=64, verbose=False):
    print("🧠 Loading model for Mesmerla...")
    start = time.time()
    llm = Llama(
        model_path=model_path,
        n_ctx=n_ctx,
        n_threads=n_threads,
        n_batch=n_batch,
        n_gpu_layers=-1,
        verbose=verbose
    )
    print(f"✅ Model loaded in {time.time() - start:.2f}s \nloaded {model_path}")
    return llm


def generate_response(
    llm,
    system_prompt,
    user_prompt,
    max_tokens=256,
    temperature=0.7,
    top_p=0.9,
    repeat_penalty=1.1,
    verbose=False,
):
    start = time.time()

    result = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        repeat_penalty=repeat_penalty,
    )

    output = result["choices"][0]["message"]["content"].strip()

    if verbose:
        print(f"⏱️ LLM response time: {time.time() - start:.2f}s")

    clear_xpu()
    return output