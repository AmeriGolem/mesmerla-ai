import os
import json

class MesmerlaMemory:
    def __init__(self, style="default", max_entries=3):
        self.style = style
        self.max_entries = max_entries
        self.entries = []

    def add(self, user_text, reply_text):
        self.entries.append({
            "user": user_text.strip(),
            "response": reply_text.strip()
        })
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[-self.max_entries:]

    def get_memory_block(self, max_tokens=300):
        memory = []
        total_tokens = 0
        for entry in reversed(self.entries):  # Start from newest
            text = f"User: {entry['user']}\nMesmerla: {entry['response']}"
            token_estimate = len(text.split()) // 0.75  # estimate 1.33 words/token
            if total_tokens + token_estimate > max_tokens:
                break
            memory.insert(0, text)
            total_tokens += token_estimate
        return "\n".join(memory)


    def save(self, directory="memory_logs",verbose:bool= False):
        os.makedirs(directory, exist_ok=True)
        path = os.path.join(directory, f"mesmerla_memory_{self.style}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.entries, f, indent=2, ensure_ascii=False)
        if verbose:
            print(f"💾 Memory saved to {path}")

    def load(self, style=None, directory="memory_logs", verb:bool=False):
        style = style or self.style
        path = os.path.join(directory, f"mesmerla_memory_{style}.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                self.entries = json.load(f)
            if verb:
                print(f"📂 Loaded memory from {path}")
        else:
            print(f"⚠️ No memory file found for style '{style}'")
            self.entries = []

    def reset(self):
        self.entries = []
        self.save(verbose=True)
        print("🧹 Memory cleared.")
