from fastapi import FastAPI
from app.api.v1.router import api_router
from app.db.session import AsyncSessionLocal
from app.db.models.user import User
from app.core.security import get_password_hash

app = FastAPI(title="AI Report Backend", version="0.1.0")
app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def seed_user():
    async with AsyncSessionLocal() as s:
        # 이미 있으면 패스
        exists = (await s.execute(
            __import__("sqlalchemy").select(User).where(User.email=="user@test.com")
        )).scalar_one_or_none()
        if not exists:
            s.add(User(email="user@test.com", password_hash=get_password_hash("pass1234"), role="user"))
            await s.commit()

from app.db.models.report import Department

@app.on_event("startup")
async def seed_departments():
    async with AsyncSessionLocal() as s:
        names = ["시설팀", "전산정보원", "환경미화", "보안관리", "학생지원"]
        for n in names:
            exists = (await s.execute(
                __import__("sqlalchemy").select(Department).where(Department.name==n)
            )).scalar_one_or_none()
            if not exists:
                s.add(Department(name=n))
        await s.commit()


@app.get("/")
def root():
    return {"service": "ai-report-backend", "status": "ok"}
