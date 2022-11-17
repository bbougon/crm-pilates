from typing import Any

from crm_pilates.domain.services import CipherService, encrypt


class MyDummyEncryptionService(CipherService):
    def decrypt(self, encrypt_content: bytes) -> bytes:
        return bytes(encrypt_content.decode("utf-8"), "utf-8")

    def encrypt(self, content: Any) -> bytes:
        return bytes(content, "utf-8")


def test_encrypt_model():
    def inner_func():
        def other_func():
            return {
                "key_with_clear_value": "clear_value",
                "key_with_encrypted_value_1": "value_to_encrypt_1",
                "key_with_encrypted_value_2": "value_to_encrypt_2",
            }

        return other_func

    function = encrypt(
        model={"keys": ["key_with_encrypted_value_1", "key_with_encrypted_value_2"]}
    )
    encrypted_model = function(inner_func())()

    assert encrypted_model == {
        "key_with_clear_value": "clear_value",
        "key_with_encrypted_value_1": "encrypted_value_to_encrypt_1",
        "key_with_encrypted_value_2": "encrypted_value_to_encrypt_2",
    }
