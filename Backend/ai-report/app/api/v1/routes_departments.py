from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/departments", tags=["departments"])

class Department(BaseModel):
    id: int
    name: str

departments = [
    {"id": 1, "name": "전산팀"},
    {"id": 2, "name": "시설팀"},
    {"id": 3, "name": "환경팀"},
    {"id": 4, "name": "학생지원팀"},
    {"id": 5, "name": "보안팀"},
]

@router.get("/", response_model=list[Department])
def get_departments():
    return departments
