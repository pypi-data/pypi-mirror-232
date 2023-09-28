import hashlib
from cryptography.fernet import Fernet

def generate_key():
    # Generate a random encryption key
    return Fernet.generate_key()

def encrypt(data, key):
    cipher_suite = Fernet(key)
    encrypted_data = cipher_suite.encrypt(data.encode())
    return encrypted_data

def decrypt(encrypted_data, key):
    cipher_suite = Fernet(key)
    decrypted_data = cipher_suite.decrypt(encrypted_data).decode()
    return decrypted_data
