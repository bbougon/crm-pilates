import functools
from abc import abstractmethod, ABCMeta
from typing import Any


class CipherService(metaclass=ABCMeta):
    @abstractmethod
    def encrypt(self, content: Any) -> bytes:
        ...

    @abstractmethod
    def decrypt(self, encrypt_content: bytes) -> bytes:
        pass


class CipherServiceProvider:
    service: CipherService


def encrypt(model: dict):
    def encrypt_func(func) -> Any:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            for key in model["keys"]:
                encrypted_content = CipherServiceProvider.service.encrypt(
                    content=result[key]
                )
                result[key] = f"{encrypted_content.decode('utf-8')}"
            return result

        return wrapper

    return encrypt_func
