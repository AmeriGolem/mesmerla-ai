from llama_cpp import Llama
import time

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
    prompt, 
    max_tokens=256, 
    temperature=0.7, 
    top_p=0.9, 
    repeat_penalty=1.1,
    verbose=False
):
    start = time.time()
    result = llm(
        prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        repeat_penalty=repeat_penalty,
        stop=["User:", "Mesmerla:", "Mesmerlo:", "Hu Tao:", "\n\n"],
    )
    output = result["choices"][0]["text"].strip()
    if verbose:
        print(f"⏱️ LLM response time: {time.time() - start:.2f}s")
    return output