
from pydantic import BaseModel, Field
from typing import List, Optional, Literal

Classes = Literal["시설","환경","전산","기타"]

class ClassifyIn(BaseModel):
    text: str

class Evidence(BaseModel):
    keywords: List[str] = []
    rule_matched: Optional[str] = None

class ClassifyOut(BaseModel):
    type: Classes
    department_id: int
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: Evidence

class RouteOut(BaseModel):
    routed_to: Literal["llm_router","human_triage"]
    reason: str
    original: Optional[ClassifyOut] = None

class LoginIn(BaseModel):
    username: str
    password: str

class LoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
