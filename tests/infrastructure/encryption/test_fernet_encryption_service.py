from crm_pilates.infrastructure.encryption.fernet_encryption_service import (
    FernetCipherService,
)
from crm_pilates.settings import config
from cryptography.fernet import Fernet


def test_should_encrypt_content():
    encrypted_content = FernetCipherService(config("SECRET_ENCRYPTION_KEY")).encrypt(
        "my content"
    )

    assert (
        Fernet(config("SECRET_ENCRYPTION_KEY")).decrypt(encrypted_content)
        == b"my content"
    )


def test_should_decrypt_content():
    encrypt_content = Fernet(config("SECRET_ENCRYPTION_KEY")).encrypt(
        b"unencrypted content"
    )

    decrypted_content = FernetCipherService(config("SECRET_ENCRYPTION_KEY")).decrypt(
        encrypt_content
    )

    assert decrypted_content == b"unencrypted content"
