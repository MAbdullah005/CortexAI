import hashlib

def hash_bytes(data: bytes):
    return hashlib.md5(data).hexdigest()

def hash_string(text: str):
    return hashlib.md5(text.encode()).hexdigest()