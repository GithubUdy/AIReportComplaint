
import os, jwt, redis.asyncio as redis
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

JWT_SECRET = os.getenv("JWT_SECRET","changeme")
ALGO = "HS256"
security = HTTPBearer()

REDIS_URL = os.getenv("REDIS_URL","redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

def create_access_token(sub: str, minutes:int=60):
    payload = {"sub": sub, "exp": datetime.utcnow()+timedelta(minutes=minutes)}
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGO)

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(creds.credentials, JWT_SECRET, algorithms=[ALGO])
        return payload["sub"]
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

async def get_cache():
    return redis_client
DB_URL = os.getenv("DB_URL", "sqlite:///./test.db")  # 기본값: SQLite
engine = create_engine(DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()