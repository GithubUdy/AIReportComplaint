
from fastapi import APIRouter, HTTPException
from .schemas import LoginIn, LoginOut
from .deps import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=LoginOut)
def login(payload: LoginIn):
    if not (payload.username=="admin" and payload.password=="admin123!"):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": create_access_token(payload.username)}
