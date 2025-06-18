import hashlib
import os

CACHE_DIR = os.path.join("mnt", "data", "gpt_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

def generate_cache_key(topic, unit_number, text):
    base = f"{topic}-{unit_number}-{text}"
    return hashlib.sha256(base.encode()).hexdigest()

def load_from_cache(key):
    path = os.path.join(CACHE_DIR, f"{key}.txt")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return None

def save_to_cache(key, content):
    path = os.path.join(CACHE_DIR, f"{key}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)