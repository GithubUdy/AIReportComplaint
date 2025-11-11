# app/services/ml.py
import random
from pydantic import BaseModel

class ClassifyResult(BaseModel):
    type: str
    department_id: int
    confidence: float

def classify_text(content: str) -> ClassifyResult:
    # ⚠️ 실제 모델 연결 전 임시 로직(키워드 매칭)
    rules = [
        ("전산", 1, "it"),
        ("화장실", 2, "facility"),
        ("누수", 2, "facility"),
        ("쓰레기", 3, "environment"),
        ("보안", 5, "security"),
        ("학생", 4, "student"),
    ]
    for k, dept_id, typ in rules:
        if k in content:
            return ClassifyResult(type=typ, department_id=dept_id, confidence=round(random.uniform(0.8,0.99),2))
    return ClassifyResult(type="general", department_id=1, confidence=0.6)
