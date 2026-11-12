import hashlib
import hmac
import base64
import json
import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from app.core.config import settings

def _hash_password_salt(password: str, salt: bytes = None) -> str:
    """Hash password using PBKDF2-HMAC-SHA256 with 100,000 iterations and salt."""
    if salt is None:
        salt = os.urandom(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return f"{salt.hex()}${hashed.hex()}"

def get_password_hash(password: str) -> str:
    return _hash_password_salt(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        salt_hex, hash_hex = hashed_password.split("$")
        salt = bytes.fromhex(salt_hex)
        expected_hash = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, 100_000).hex()
        return hmac.compare_digest(hash_hex, expected_hash)
    except Exception:
        return False

def _b64_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")

def _b64_decode(data: str) -> bytes:
    padding = "=" * (4 - len(data) % 4) if len(data) % 4 != 0 else ""
    return base64.urlsafe_b64decode((data + padding).encode("utf-8"))

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Creates a signed HMAC-SHA256 JWT-compatible access token."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    header = {"alg": "HS256", "typ": "JWT"}
    to_encode.update({"exp": int(expire.timestamp()), "iat": int(now.timestamp())})
    
    header_b64 = _b64_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64_encode(json.dumps(to_encode, separators=(",", ":")).encode("utf-8"))
    
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    signature = hmac.new(settings.SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
    signature_b64 = _b64_encode(signature)
    
    return f"{header_b64}.{payload_b64}.{signature_b64}"

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodes and validates HMAC-SHA256 JWT token."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_b64, payload_b64, signature_b64 = parts
        
        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
        expected_sig = hmac.new(settings.SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
        actual_sig = _b64_decode(signature_b64)
        
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None
        
        payload_bytes = _b64_decode(payload_b64)
        payload = json.loads(payload_bytes.decode("utf-8"))
        
        exp = payload.get("exp")
        if exp and datetime.now(timezone.utc).timestamp() > exp:
            return None # Expired
            
        return payload
    except Exception:
        return None
