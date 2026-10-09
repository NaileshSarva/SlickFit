"""Unit tests for cryptographic security, password hashing, and token signing."""

import datetime as dt
import time

import pytest

from src.slickfit.auth.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hashing_and_verification():
    plain = "SuperSecretAthletePass2026!"
    hashed = hash_password(plain)

    assert hashed.startswith("pbkdf2_sha256$600000$")
    assert verify_password(plain, hashed) is True
    assert verify_password("WrongPassword123!", hashed) is False
    assert verify_password("", hashed) is False


def test_password_hash_uniqueness_with_salt():
    plain = "SamePassword"
    hash1 = hash_password(plain)
    hash2 = hash_password(plain)

    # Different salts must produce distinct hashes
    assert hash1 != hash2
    assert verify_password(plain, hash1) is True
    assert verify_password(plain, hash2) is True


def test_token_creation_and_decoding():
    subject = "user-uuid-1234-5678"
    claims = {"email": "runner@slickfit.local", "is_demo": True}
    token = create_access_token(subject, claims=claims)

    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == subject
    assert decoded["email"] == "runner@slickfit.local"
    assert decoded["is_demo"] is True


def test_tampered_token_is_rejected():
    token = create_access_token("valid-user-id")
    parts = token.split(".")

    # Tamper with payload
    tampered_token = f"{parts[0]}.eyJzdWIiOiAiaGFja2VyIn0.{parts[2]}"
    assert decode_access_token(tampered_token) is None


def test_expired_token_is_rejected():
    # Issue a token expired 5 seconds ago
    token = create_access_token(
        subject="expired-user",
        expires_delta=dt.timedelta(seconds=-5),
    )
    assert decode_access_token(token) is None


def test_signed_token_with_wrong_algorithm_header_is_rejected():
    import base64
    import hashlib
    import hmac
    import json
    from src.slickfit.config import settings

    payload = {"sub": "user-1", "iat": 1, "exp": int(time.time()) + 60}
    encode = lambda obj: base64.urlsafe_b64encode(json.dumps(obj, separators=(",", ":")).encode()).rstrip(b"=").decode()
    header = encode({"alg": "none", "typ": "JWT"})
    body = encode(payload)
    message = f"{header}.{body}".encode("ascii")
    signature = base64.urlsafe_b64encode(hmac.new(settings.secret_key.encode(), message, hashlib.sha256).digest()).rstrip(b"=").decode()
    assert decode_access_token(f"{header}.{body}.{signature}") is None
