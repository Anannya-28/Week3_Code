

"""
Password hashing and background-safe audit log writer.
"""

import hashlib
import hmac
import logging
import secrets

logger = logging.getLogger("online_shopping.utils")


#  Password helpers 

def hash_password(password: str) -> str:
    """PBKDF2-HMAC-SHA256 with a random 16-byte salt."""
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt, 120_000
    )
    return f"{salt.hex()}${digest.hex()}"


def verify_password(plain: str, stored: str) -> bool:
    """Constant-time comparison — prevents timing attacks."""
    try:
        salt_hex, digest_hex = stored.split("$", 1)
        expected = hashlib.pbkdf2_hmac(
            "sha256",
            plain.encode(),
            bytes.fromhex(salt_hex),
            120_000,
        )
        return hmac.compare_digest(expected.hex(), digest_hex)
    except (ValueError, TypeError):
        return False


# Background audit log writer

def write_audit_log(
    user_id: int | None,
    action: str,
    entity: str | None = None,
    entity_id: int | None = None,
    message: str | None = None,
) -> None:
    """
    Fire-and-forget audit log writer.
    Runs in a thread pool via FastAPI BackgroundTasks.

    WHY SYNC:
    This is a simple single-table DB insert with no external calls.
    Running it sync in a background thread avoids async complexity
    while still being non-blocking to the HTTP response.
    """
    # Late import to avoid circular dependency at module load time
    from core.database import _SyncSession
    from modules.users.model import AuditLog

    db = _SyncSession()
    try:
        db.add(AuditLog(
            user_id=user_id,
            action=action,
            entity=entity,
            entity_id=entity_id,
            message=message,
        ))
        db.commit()
        logger.info(
            "AUDIT | action=%s | entity=%s | id=%s | user=%s",
            action, entity, entity_id, user_id,
        )
    except Exception as exc:
        db.rollback()
        logger.error("AUDIT WRITE FAILED | %s", exc, exc_info=True)
    finally:
        db.close()
