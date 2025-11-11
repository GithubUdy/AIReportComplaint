"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import json
from pathlib import Path

from ..schemas import ClassifyIn, ClassifyOut, RouteOut, Evidence
from ..services.model import predict, label_to_department, make_evidence
from ..services.rules import THRESHOLD, apply_keyword_rules
from ..deps import get_cache, get_db

# (옵션) LLM 라우터가 없으면 자동 폴백
try:
    from ..services.llm_router import llm_route  # Gemini/OpenAI 등
except Exception:  # 파일이 없거나 의존성이 없을 때
    async def llm_route(text: str):
        return {"label": None, "reason": "llm_disabled"}

# (옵션) DB 로깅이 없으면 폴백
try:
    from ..db import PredictionLog
except Exception:
    PredictionLog = None  # type: ignore

router = APIRouter(prefix="/ml", tags=["ml"])


@router.post("/classify", response_model=ClassifyOut)
async def classify(
    body: ClassifyIn,
    cache=Depends(get_cache),
    db: Session = Depends(get_db),
):
    text = body.text.strip()
    key = f"classify:{text}"

    # 캐시 읽기: Redis 미가동이어도 에러 없이 지나가도록
    try:
        cached = await cache.get(key)
        if cached:
            return ClassifyOut(**json.loads(cached))
    except Exception as e:
        print("cache get skipped:", e)

    # 모델 예측
    label, conf = predict(text)
    ev = make_evidence(text, label)
    out = ClassifyOut(
        type=label,
        department_id=label_to_department(label),
        confidence=conf,
        evidence=Evidence(keywords=ev),
    )

    # 캐시 쓰기 (실패 무시)
    try:
        await cache.set(key, out.model_dump_json(), ex=300)
    except Exception as e:
        print("cache set skipped:", e)

    # DB 로깅 (선택)
    if PredictionLog is not None:
        try:
            db.add(PredictionLog(text=text, predicted_label=out.type, confidence=str(out.confidence)))
            db.commit()
        except Exception as e:
            print("db log failed:", e)
            db.rollback()

    return out


@router.post("/route", response_model=RouteOut)
async def route(body: ClassifyIn):
    # 1차: 모델 예측
    label, conf = predict(body.text)

    # 신뢰도 낮으면(THRESHOLD 미만) → 키워드 룰 → LLM 순으로 보강
    if conf < THRESHOLD:
        # 2차: 키워드 룰
        rule = apply_keyword_rules(body.text)
        if rule and rule != label:
            alt = ClassifyOut(
                type=rule,
                department_id=label_to_department(rule),
                confidence=0.51,
                evidence=Evidence(keywords=[], rule_matched="keyword"),
            )
            return RouteOut(routed_to="human_triage", reason=f"low confidence {conf:.2f}", original=alt)

        # 3차: LLM 라우터(설정 시)
        try:
            lr = await llm_route(body.text)
        except Exception as e:
            lr = {"label": None, "reason": f"llm_error:{type(e).__name__}"}

        if lr.get("label"):
            alt = ClassifyOut(
                type=lr["label"],
                department_id=label_to_department(lr["label"]),
                confidence=0.60,
                evidence=Evidence(keywords=[], rule_matched="llm"),
            )
            return RouteOut(routed_to="human_triage", reason=f"llm:{lr.get('reason','ok')}", original=alt)

        # LLM도 실패 → LLM 라우터로 폴백 표기
        return RouteOut(routed_to="llm_router", reason=f"low confidence {conf:.2f}", original=None)

    # 신뢰도 충분 → 알파 단계에서는 최종 전에 수동 검토로 보냄
    return RouteOut(routed_to="human_triage", reason="alpha stage manual check", original=None)


@router.get("/metrics")
async def metrics():
    p = Path(__file__).resolve().parents[2] / "models" / "metrics.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"detail": "metrics not found"}
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
import json
from pathlib import Path

from ..schemas import ClassifyIn, ClassifyOut, RouteOut, Evidence
from ..services.model import predict, label_to_department, make_evidence
from ..services.rules import THRESHOLD, apply_keyword_rules
from ..deps import get_cache, get_db

# (옵션) LLM 라우터가 없으면 자동 폴백
try:
    from ..services.llm_router import llm_route  # Gemini/OpenAI 등
except Exception:  # 파일이 없거나 의존성이 없을 때
    async def llm_route(text: str):
        return {"label": None, "reason": "llm_disabled"}

# (옵션) DB 로깅이 없으면 폴백
try:
    from ..db import PredictionLog
except Exception:
    PredictionLog = None  # type: ignore

router = APIRouter(prefix="/ml", tags=["ml"])


@router.post("/classify", response_model=ClassifyOut)
async def classify(
    body: ClassifyIn,
    cache=Depends(get_cache),
    db: Session = Depends(get_db),
):
    text = body.text.strip()
    key = f"classify:{text}"

    # 캐시 읽기(실패 무시)
    try:
        cached = await cache.get(key)
        if cached:
            return ClassifyOut(**json.loads(cached))
    except Exception as e:
        print("cache get skipped:", e)

    # 모델 예측
    label, conf = predict(text)
    ev = make_evidence(text, label)
    out = ClassifyOut(
        type=label,
        department_id=label_to_department(label),
        confidence=conf,
        evidence=Evidence(keywords=ev),
    )

    # 캐시 쓰기(실패 무시)
    try:
        await cache.set(key, out.model_dump_json(), ex=300)
    except Exception as e:
        print("cache set skipped:", e)

    # DB 로깅(선택)
    if PredictionLog is not None:
        try:
            db.add(PredictionLog(text=text, predicted_label=out.type, confidence=str(out.confidence)))
            db.commit()
        except Exception as e:
            print("db log failed:", e)
            db.rollback()

    return out


@router.post("/route", response_model=RouteOut)
async def route(
    body: ClassifyIn,
    force_llm: bool = Query(False, description="테스트용: LLM을 강제로 한 번 시도"),
):
    # 1차: 모델 예측
    label, conf = predict(body.text)

    # 2차: 임계값 미만이거나 강제 호출이면 → 키워드 룰 → LLM 순으로 보강
    if conf < THRESHOLD or force_llm:
        # (옵션) 키워드 룰: 강제 호출 중엔 생략하고 바로 LLM 시도하고 싶다면 아래 if를 주석 처리
        rule = apply_keyword_rules(body.text)
        if rule and rule != label and not force_llm:
            alt = ClassifyOut(
                type=rule,
                department_id=label_to_department(rule),
                confidence=0.51,
                evidence=Evidence(keywords=[], rule_matched="keyword"),
            )
            return RouteOut(routed_to="human_triage", reason=f"low confidence {conf:.2f}", original=alt)

        # LLM 시도(항상 한 번 실행)
        try:
            lr = await llm_route(body.text)
        except Exception as e:
            lr = {"label": None, "reason": f"llm_error:{type(e).__name__}"}

        print("LLM route →", lr)  # 콘솔 진단용

        if lr.get("label"):
            alt = ClassifyOut(
                type=lr["label"],
                department_id=label_to_department(lr["label"]),
                confidence=0.60,
                evidence=Evidence(keywords=[], rule_matched="llm"),
            )
            return RouteOut(routed_to="human_triage", reason=f"llm:{lr.get('reason','ok')}", original=alt)

        # LLM 실패 → 실패 사유를 reason에 그대로 노출
        return RouteOut(routed_to="llm_router", reason=f"llm:{lr.get('reason','unknown')}", original=None)

    # 신뢰도 충분 → 알파 단계 수동 검토
    return RouteOut(routed_to="human_triage", reason="alpha stage manual check", original=None)


@router.get("/metrics")
async def metrics():
    p = Path(__file__).resolve().parents[2] / "models" / "metrics.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"detail": "metrics not found"}
