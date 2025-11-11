
from fastapi import APIRouter, Depends, UploadFile, File, Form
from ..deps import get_current_user
from ..services.notify import send_mail

router = APIRouter(prefix="/reports", tags=["reports"])

@router.post("/submit")
async def submit_report(
    title: str = Form(...),
    content: str = Form(...),
    file: UploadFile | None = File(None),
    user=Depends(get_current_user)
):
    await send_mail("helpdesk@campus.local", f"[신고] {title}", content[:1000])
    return {"ok": True, "file_received": bool(file), "user": user}
