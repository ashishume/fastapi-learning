import hashlib
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_pass: str) -> str:
    # Pre-hash with SHA-256 to handle passwords longer than 72 bytes
    # SHA-256 produces a fixed-length 64-character hex string
    prehashed = hashlib.sha256(plain_pass.encode('utf-8')).hexdigest()
    return pwd_context.hash(prehashed)


def verify_password(plain_pass: str, hashed_pass: str) -> bool:
    # Pre-hash the plain password the same way before verification
    prehashed = hashlib.sha256(plain_pass.encode('utf-8')).hexdigest()
    return pwd_context.verify(prehashed, hashed_pass)
