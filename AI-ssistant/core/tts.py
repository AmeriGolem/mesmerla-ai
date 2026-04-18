import socket
import json
import time
import winsound
import subprocess
import os


def speak_as_mesmerla(
    text, 
    ref_audio_path="", 
    ref_text_path="", 
    output_path=""
):
    request = {
        "text": text,
        "ref_audio": ref_audio_path,
        "ref_text": ref_text_path,
        "output_path": output_path
    }

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("localhost", 65432))
            s.sendall(json.dumps(request).encode("utf-8"))
            response = s.recv(4096)
            response_data = json.loads(response.decode("utf-8"))
            return response_data
    except Exception as e:
        return {"status": "error", "reason": str(e)}


"""def boot_mesmerla(gpt_path, sovits_path, verbose=True):
    from inference_webui import change_gpt_weights, change_sovits_weights

    if verbose:
        print("🌙 Awakening Mesmerla...\n")

    start = time.time()
    if verbose:
        print("🔁 Loading GPT model...", end=" ")
    change_gpt_weights(gpt_path)
    if verbose:
        print(f"✅ Done in {time.time() - start:.2f}s")

    start = time.time()
    if verbose:
        print("🔁 Loading SoVITS model...", end=" ")
    hps = change_sovits_weights(sovits_path)
    if verbose:
        print(f"✅ Done in {time.time() - start:.2f}s")

    if verbose:
        print("\n✨ Mesmerla is online. Ready to speak.\n")

    return hps"""


def play_audio(path):
    winsound.PlaySound(path, winsound.SND_FILENAME)
    
def start_mesmerla_server_with_log():
    venv_python = r"C:\\Users\\aberl\\Desktop\\Projet Code\\Mesmerla_AI\\mesmerla-gpt-sovits_venv\\Scripts\\python.exe"
    server_script = r"C:\\Users\\aberl\\Desktop\\Projet Code\\Mesmerla_AI\\GPT-SoVITS\\GPT_SoVITS\\mesmerla_socket_server.py"
    working_dir = r"C:\\Users\\aberl\\Desktop\\Projet Code\\Mesmerla_AI\\GPT-SoVITS"
    log_path = r"C:\\Users\\aberl\\Desktop\\Projet Code\\Mesmerla_AI\\AI-ssistant\\mesmerla_server.log"

    clean_env = os.environ.copy()
    clean_env.pop("MPLBACKEND", None)

    print(f"📜 Logging Mesmerla server output to: {log_path}")
    log_file = open(log_path, "w")

    try:
        process = subprocess.Popen(
            [venv_python, server_script],
            stdout=log_file,
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW,
            env=clean_env,
            cwd=working_dir
        )
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return None, log_path

    print("⏳ Waiting for Mesmerla server to respond...")

    try:
        with open(log_path, "r", encoding="utf-8") as f:
            while True:
                content = f.read()
                if content.strip():
                    print("🟢 Server responded. Check log for details.")
                    break
    except Exception as e:
        print(f"❌ Error reading log: {e}")

    return process, log_path


# Automatically start the server upon import
_server_process, _server_log = start_mesmerla_server_with_log()

def stop_mesmerla_server():
    global _server_process
    if _server_process and _server_process.poll() is None:
        _server_process.terminate()
        print("🛑 Mesmerla server terminated.")
    else:
        print("⚠️ No active server process to terminate.")
