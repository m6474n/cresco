from cryptography.fernet import Fernet
from app.config import Config


class CryptoService:
    @staticmethod
    def get_cipher():
        key = Config.ENCRYPTION_KEY
        if not key:
            raise ValueError("ENCRYPTION_KEY is not configured.")
        return Fernet(key.encode() if isinstance(key, str) else key)

    @classmethod
    def encrypt(cls, plaintext: str) -> str:
        if not plaintext:
            return ""
        cipher = cls.get_cipher()
        return cipher.encrypt(plaintext.encode("utf-8")).decode("utf-8")

    @classmethod
    def decrypt(cls, ciphertext: str) -> str:
        if not ciphertext:
            return ""
        cipher = cls.get_cipher()
        return cipher.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
