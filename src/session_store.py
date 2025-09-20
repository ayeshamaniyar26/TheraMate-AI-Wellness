# session_store.py
import os, json
from cryptography.fernet import Fernet

KEY_PATH = "data/session_key.key"
STORE_PATH = "data/sessions.json"

def _load_key():
    if not os.path.exists(KEY_PATH):
        k = Fernet.generate_key()
        with open(KEY_PATH,"wb") as f:
            f.write(k)
    else:
        with open(KEY_PATH,"rb") as f:
            k = f.read()
    return k

fernet = Fernet(_load_key())

def save_session(session_id: str, payload: dict):
    os.makedirs("data", exist_ok=True)
    data = {}
    if os.path.exists(STORE_PATH):
        with open(STORE_PATH,"rb") as f:
            enc = f.read()
            data = json.loads(fernet.decrypt(enc).decode())
    data[session_id] = payload
    enc = fernet.encrypt(json.dumps(data).encode())
    with open(STORE_PATH,"wb") as f:
        f.write(enc)

def load_session(session_id: str):
    if not os.path.exists(STORE_PATH):
        return {}
    with open(STORE_PATH,"rb") as f:
        enc = f.read()
        data = json.loads(fernet.decrypt(enc).decode())
    return data.get(session_id, {})
