# admin_login.py
import hashlib
import os 

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Zugangsdaten
ADMIN_USERNAME = "admin"

# Hash aus Datei laden
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HASH_FILE = os.path.join(BASE_DIR, "admin.hash")

with open(HASH_FILE, "r") as f:
    ADMIN_PASSWORD_HASH = f.read().strip()

def check_admin_login(username: str, password: str) -> bool:
    return username == ADMIN_USERNAME and hash_password(password) == ADMIN_PASSWORD_HASH


