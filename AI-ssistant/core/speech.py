import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import winsound
from pynput import keyboard
from faster_whisper import WhisperModel

model = None
stop_flag = False

fs = 44100

def get_whisper_model():
    global model
    if model is None:
        model = WhisperModel(
            r"AI-ssistant\models\faster-whisper-small",
            device="cpu", 
            compute_type="int8"
        )
    return model

# ---  Recording  ---
def on_key_press(key):
    global stop_flag
    try:
        if key == keyboard.Key.space or key == keyboard.Key.enter:
            print("🛑 Touche pressée. Arrêt manuel.")
            stop_flag = True
            
            return False  # stop the listener
    except:
        pass

def record_audio(filename=r"AI-ssistant\input\audio_input.wav", fs=44100, silence_threshold=2500, max_silence_duration=0.75):
    global stop_flag
    stop_flag = False
    buffer = []
    silence_counter = 0
    frame_duration = 0.2
    frame_size = int(fs * frame_duration)
    has_started_speaking = False  # ← This is the key addition
    
    # Clavier en parallèle
    listener = keyboard.Listener(on_press=on_key_press)
    listener.start()

    

    try:
        with sd.InputStream(samplerate=fs, channels=1, dtype='int16') as stream:
            print("🎙️ Parle quand tu veux. Appuie sur [Entrée], ou [Espace] pour arrêter manuellement.")
            while not stop_flag:
                data, _ = stream.read(frame_size)
                volume = np.linalg.norm(data)
                buffer.append(data)
                #print("volue:", volume)
                if not has_started_speaking:
                    if volume >= silence_threshold:
                        has_started_speaking = True
                        silence_counter = 0  # start tracking silence only now
                else:
                    if volume < silence_threshold:
                        silence_counter += frame_duration
                        if silence_counter >= max_silence_duration:
                            print("🔇 Silence détecté... fin de l'enregistrement.")
                            break
                    else:
                        silence_counter = 0
    except Exception as e:
        print("❌ Erreur micro :", e)
        return

    listener.stop()
    audio = np.concatenate(buffer, axis=0)
    write(filename, fs, audio)
    print("✅ Audio sauvegardé dans", filename)
    
# --- Transcription ---
def transcribe_audio(file_path=r"C:\Users\aberl\Desktop\Projet Code\Mesmerla_AI\AI-ssistant\input\audio_input.wav"):
    model = get_whisper_model()
    segments, info = model.transcribe(file_path)

    text = ""
    for segment in segments:
        text += segment.text

    return text.strip()

# --- Playback ---
def play_audio(path= r"C:\Users\aberl\Desktop\Projet Code\Mesmerla_AI\AI-ssistant\output\mesmerla_out.wav"):
    winsound.PlaySound(path, winsound.SND_FILENAME)