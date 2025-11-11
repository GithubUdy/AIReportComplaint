from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional

from app.db.session import get_db
from app.db.models.report import Report, ReportComment, ReportFile
from app.db.schemas.report import ReportCreate, ReportUpdate, ReportOut, CommentCreate, CommentOut, FileOut
from app.core.deps import get_current_user
from app.core.mail import send_email

# ML 분류기 (내부 라우트의 함수 재사용)
from app.api.v1.routes_ml import router as ml_router  # for prefix 보장
from app.api.v1.routes_ml import classify as local_classify, ClassifyRequest

router = APIRouter(prefix="/reports", tags=["reports"])

def _dept_email(dept_id: int) -> str:
    return {
        1: "it@example.com",
        2: "facility@example.com",
        3: "env@example.com",
        4: "student@example.com",
        5: "security@example.com",
    }.get(dept_id, "it@example.com")

@router.post("", response_model=ReportOut)
async def create_report(
    payload: ReportCreate,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
    auto_classify: bool = Query(False),
    background_tasks: BackgroundTasks = None,
):
    # 1) auto_classify가 true일 때만 임시 분류기 호출
    clf_type = None
    clf_dept = None
    if auto_classify:
        clf_res = local_classify(ClassifyRequest(content=payload.content))
        # local_classify는 동기 함수(pydantic 모델 반환). 필드 꺼내기
        clf_type = getattr(clf_res, "type", None)
        clf_dept = getattr(clf_res, "department_id", None)

    # 2) 최종 type/department_id 결정 (사용자 입력 > 자동분류 > 기본값)
    final_type = payload.type or clf_type or "general"
    final_dept = payload.department_id if payload.department_id is not None else (clf_dept or 1)

    report = Report(
        title=payload.title,
        content=payload.content,
        type=final_type,
        department_id=final_dept,
        reporter_email=getattr(user, "email", "anonymous@test.com"),
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)

    # 3) 이메일 알림 (비동기 권장: BackgroundTasks)
    if background_tasks is not None:
        background_tasks.add_task(
            send_email,
            subject=f"[신규 신고] #{report.id} {report.title}",
            email_to=_dept_email(report.department_id),
            body=(
                f"신고 ID: {report.id}\n"
                f"제목: {report.title}\n"
                f"내용: {report.content}\n"
                f"유형: {report.type}\n"
                f"담당부서ID: {report.department_id}\n"
                f"신고자: {report.reporter_email}\n"
            ),
        )
    else:
        # BackgroundTasks 주입이 안 된 경우라도 서비스 진행
        try:
            await send_email(
                subject=f"[신규 신고] #{report.id} {report.title}",
                email_to=_dept_email(report.department_id),
                body=(
                    f"신고 ID: {report.id}\n"
                    f"제목: {report.title}\n"
                    f"내용: {report.content}\n"
                    f"유형: {report.type}\n"
                    f"담당부서ID: {report.department_id}\n"
                    f"신고자: {report.reporter_email}\n"
                ),
            )
        except Exception:
            pass

    return report
