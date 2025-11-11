from pydantic import BaseModel, Field
from typing import Optional, List

class ReportCreate(BaseModel):
    title: str
    content: str
    type: str = "general"
    department_id: Optional[int] = None

class ReportUpdate(BaseModel):
    # 작성자: title/content만 변경
    title: Optional[str] = None
    content: Optional[str] = None
    # 관리자는 아래 2개도 변경 가능
    status: Optional[str] = None
    department_id: Optional[int] = None

class ReportOut(BaseModel):
    id: int
    title: str
    content: str
    type: str
    status: str
    department_id: Optional[int]
    reporter_email: str
    class Config: from_attributes = True

class CommentCreate(BaseModel):
    content: str = Field(min_length=1)

class CommentOut(BaseModel):
    id: int
    content: str
    author_email: str
    class Config: from_attributes = True

class FileOut(BaseModel):
    id: int
    original_name: str
    mime: str
    size: int
    class Config: from_attributes = True
