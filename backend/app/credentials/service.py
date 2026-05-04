import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.config import settings
from app.shared.models import EncryptedCredential


def _get_key() -> bytes:
    return bytes.fromhex(settings.ENCRYPTION_MASTER_KEY)


def encrypt_value(plaintext: str) -> tuple[bytes, bytes, bytes]:
    key = _get_key()
    aesgcm = AESGCM(key)
    iv = os.urandom(12)
    ciphertext_and_tag = aesgcm.encrypt(iv, plaintext.encode(), None)
    ciphertext = ciphertext_and_tag[:-16]
    tag = ciphertext_and_tag[-16:]
    return ciphertext, iv, tag


def decrypt_value(encrypted_value: bytes, iv: bytes, tag: bytes) -> str:
    key = _get_key()
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(iv, encrypted_value + tag, None)
    return plaintext.decode()


async def store_credential(
    db: AsyncSession, service_name: str, value: str, updated_by=None
) -> EncryptedCredential:
    ciphertext, iv, tag = encrypt_value(value)

    result = await db.execute(
        select(EncryptedCredential).where(EncryptedCredential.service_name == service_name)
    )
    credential = result.scalar_one_or_none()

    if credential:
        credential.encrypted_value = ciphertext
        credential.iv = iv
        credential.tag = tag
        credential.updated_by = updated_by
    else:
        credential = EncryptedCredential(
            service_name=service_name,
            encrypted_value=ciphertext,
            iv=iv,
            tag=tag,
            updated_by=updated_by,
        )
        db.add(credential)

    await db.commit()
    await db.refresh(credential)
    return credential


async def get_credential(db: AsyncSession, service_name: str) -> str | None:
    result = await db.execute(
        select(EncryptedCredential).where(EncryptedCredential.service_name == service_name)
    )
    credential = result.scalar_one_or_none()
    if not credential:
        return None
    return decrypt_value(credential.encrypted_value, credential.iv, credential.tag)


async def delete_credential(db: AsyncSession, service_name: str) -> bool:
    result = await db.execute(
        select(EncryptedCredential).where(EncryptedCredential.service_name == service_name)
    )
    credential = result.scalar_one_or_none()
    if not credential:
        return False
    await db.delete(credential)
    await db.commit()
    return True


async def list_credentials(db: AsyncSession) -> list[dict]:
    result = await db.execute(select(EncryptedCredential))
    credentials = result.scalars().all()
    return [
        {
            "id": c.id,
            "service_name": c.service_name,
            "updated_at": c.updated_at,
            "has_value": True,
        }
        for c in credentials
    ]
