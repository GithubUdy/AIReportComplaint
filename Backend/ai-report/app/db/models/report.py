from sqlalchemy import String, Integer, ForeignKey, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Department(Base):
    __tablename__ = "departments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

class Report(Base):
    __tablename__ = "reports"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reporter_email: Mapped[str] = mapped_column(String(255), index=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)
    type: Mapped[str] = mapped_column(String(50), index=True, default="general")
    status: Mapped[str] = mapped_column(String(20), index=True, default="new")
    department_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id"))
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now(), index=True)

    department = relationship("Department")
    files = relationship("ReportFile", back_populates="report", cascade="all,delete-orphan")
    comments = relationship("ReportComment", back_populates="report", cascade="all,delete-orphan")

class ReportFile(Base):
    __tablename__ = "report_files"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("reports.id"), index=True)
    storage_key: Mapped[str] = mapped_column(String(500))  # 로컬: 절대경로
    original_name: Mapped[str] = mapped_column(String(255))
    mime: Mapped[str] = mapped_column(String(100), default="application/octet-stream")
    size: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now())

    report = relationship("Report", back_populates="files")

class ReportComment(Base):
    __tablename__ = "report_comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("reports.id"), index=True)
    author_email: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.now())

    report = relationship("Report", back_populates="comments")
