from typing import Any
from cryptography.fernet import Fernet

from crm_pilates.domain.services import CipherService


class FernetCipherService(CipherService):
    def __init__(self, private_key: str) -> None:
        super().__init__()
        self.fernet = Fernet(private_key)

    def encrypt(self, content: Any) -> bytes:
        return self.fernet.encrypt(bytes(content, "utf-8"))

    def decrypt(self, encrypt_content) -> bytes:
        return self.fernet.decrypt(encrypt_content)
