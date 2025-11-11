from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.schemas.auth import LoginRequest, TokenResponse
from app.core.security import verify_password, create_access_token, get_password_hash
from app.db.session import get_db
from app.db.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


# 🔹 회원가입(Register)
@router.post("/register", response_model=dict)
async def register(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    # 이미 존재하는 이메일인지 확인
    q = await db.execute(select(User).where(User.email == payload.email))
    if q.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # 비밀번호 해싱 후 저장
    hashed_pw = get_password_hash(payload.password)
    new_user = User(
        email=payload.email,
        password_hash=hashed_pw,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"message": "User registered successfully", "email": new_user.email}


# 🔹 로그인(Login)
@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(User).where(User.email == payload.email))
    user = q.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(sub=user.email)
    return TokenResponse(access_token=token)
