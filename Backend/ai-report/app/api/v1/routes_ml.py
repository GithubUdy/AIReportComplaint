# app/api/v1/routes_ml.py
from fastapi import APIRouter
from pydantic import BaseModel
import random

router = APIRouter(prefix="/ml", tags=["ml"])  # ✅ prefix 추가

class ClassifyRequest(BaseModel):
    content: str

class ClassifyResponse(BaseModel):
    type: str
    department_id: int
    confidence: float

@router.post("/classify", response_model=ClassifyResponse)
def classify(req: ClassifyRequest):
    departments = {
        "전산": (1, "it"),
        "화장실": (2, "facility"),
        "쓰레기": (3, "environment"),
        "학생": (4, "student"),
        "보안": (5, "security")
    }
    for k, v in departments.items():
        if k in req.content:
            return {"type": v[1], "department_id": v[0], "confidence": round(random.uniform(0.8, 0.99), 2)}
    return {"type": "general", "department_id": 1, "confidence": 0.6}
