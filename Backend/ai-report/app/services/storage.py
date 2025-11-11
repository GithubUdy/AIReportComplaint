from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile
from app.core.config import settings

base_dir = Path(settings.LOCAL_STORAGE_DIR)
base_dir.mkdir(parents=True, exist_ok=True)

async def save_local(file: UploadFile, prefix: str = "reports/"):
    target_dir = base_dir / prefix
    target_dir.mkdir(parents=True, exist_ok=True)
    key = f"{uuid4()}-{file.filename}"
    dest = target_dir / key
    size = 0
    with dest.open("wb") as f:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            f.write(chunk)
    await file.close()
    return str(dest.resolve()), size, file.content_type or "application/octet-stream"
