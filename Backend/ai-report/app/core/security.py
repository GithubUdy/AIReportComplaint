# app/core/security.py
import time, jwt
from passlib.context import CryptContext
from app.core.config import settings

# bcrypt_sha256를 우선으로 사용, 기존 bcrypt 해시도 검증 가능하게 같이 둠
pwd_ctx = CryptContext(
    schemes=["bcrypt_sha256", "bcrypt"],
    deprecated="auto",
)

def get_password_hash(password: str) -> str:
    return pwd_ctx.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain, hashed)

def create_access_token(sub: str, expires_in: int = 3600) -> str:
    payload = {"sub": sub, "exp": int(time.time()) + expires_in}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])

# 하위 호환 (예전에 hash_password 이름을 썼다면)
hash_password = get_password_hash
