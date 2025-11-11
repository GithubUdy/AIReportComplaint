import os, re, json
from typing import Dict, Any, Optional, List
import requests

Labels = ["시설", "환경", "전산", "기타"]

def _extract_json(text: str) -> Optional[dict]:
    for m in re.finditer(r"\{.*\}", text, flags=re.S):
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    return None

# ---- 핵심: 사용 가능한 모델/버전을 동적으로 탐색 ----
def _list_models(api_key: str) -> Dict[str, Any]:
    """
    v1 -> 실패 시 v1beta 순으로 모델 목록을 조회.
    반환: {"api_version": "v1"|"v1beta", "models": [모델명 문자열 리스트]}
    """
    bases = [("v1", "https://generativelanguage.googleapis.com/v1/models"),
             ("v1beta", "https://generativelanguage.googleapis.com/v1beta/models")]

    for ver, url in bases:
        try:
            r = requests.get(f"{url}?key={api_key}", timeout=10)
            if r.ok:
                data = r.json()
                names = [m.get("name") for m in data.get("models", []) if "name" in m]
                if names:
                    return {"api_version": ver, "models": names}
                # ok인데 리스트가 비면 계속 다음 버전 시도
            else:
                # 디버그용 로그
                print(f"[ListModels {ver}] HTTP {r.status_code} - {r.text[:200]}")
        except Exception as e:
            print(f"[ListModels {ver} Exception] {type(e).__name__}: {e}")
    return {"api_version": None, "models": []}

def _choose_model(available: List[str]) -> Optional[str]:
    """
    선호도 순으로 텍스트 생성 가능한 모델을 고름.
    available에는 'models/...' 형태로 이름이 들어있음.
    """
    # 선호도(상황에 따라 여기 순서만 바꿔도 됨)
    preferred = [
        "models/gemini-pro",                # 가장 호환 잘됨 (많은 계정에서 열려있음)
        "models/gemini-1.5-flash-latest",
        "models/gemini-1.5-flash",
        "models/gemini-1.5-pro",
        "models/gemini-1.0-pro"
    ]
    # available에 실제로 존재하는 첫 후보를 선택
    for p in preferred:
        if p in available:
            return p
    # 위 후보가 하나도 없으면, 이름에 'gemini'가 있고 generateContent 가능한 것으로 보이는 것 아무거나
    for name in available:
        if "models/gemini" in name and "embedding" not in name.lower():
            return name
    return None

async def llm_route(text: str) -> Dict[str, Any]:
    gkey = os.getenv("GEMINI_API_KEY")
    if not gkey:
        print("[LLM Router] ❌ GEMINI_API_KEY 없음")
        return {"label": None, "reason": "no_llm_key"}

    # 1) 내 키로 어떤 모델/버전이 열려있는지 먼저 확인
    probe = _list_models(gkey)
    api_ver = probe["api_version"]
    models = probe["models"]

    if not api_ver or not models:
        # 모델 목록도 못 가져오면 키/권한/네트워크 이슈
        return {"label": None, "reason": "gemini_listmodels_failed"}

    chosen = _choose_model(models)
    if not chosen:
        print("[Gemini] ❌ 사용 가능한 텍스트 생성 모델을 찾지 못했습니다.")
        # 디버그: 사용 가능한 모델 나열
        print("[Gemini] available models (truncated):", models[:10])
        return {"label": None, "reason": "gemini_no_suitable_model"}

    # 2) 선택한 모델로 generateContent 호출
    try:
        # chosen 예: "models/gemini-pro"
        url = f"https://generativelanguage.googleapis.com/{api_ver}/{chosen}:generateContent?key={gkey}"

        prompt = (
            "다음 한국어 신고 문장을 읽고 가장 적절한 하나의 카테고리를 선택하세요.\n"
            f"카테고리 후보: {', '.join(Labels)}\n"
            "출력 형식(JSON): {\"label\":\"시설|환경|전산|기타\", \"reason\":\"...\"}\n"
            f"문장: {text}\n"
        )
        data = {"contents": [{"parts": [{"text": prompt}]}]}

        r = requests.post(url, json=data, timeout=20)
        if not r.ok:
            print(f"[Gemini Error] ❌ HTTP {r.status_code} - {r.text[:200]}")
            return {"label": None, "reason": f"gemini_http_{r.status_code}"}

        resp = r.json()
        # 응답 스키마 수비적으로 접근
        content = (
            resp.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
        )

        parsed = _extract_json(content) or {}
        if parsed.get("label") in Labels:
            return {"label": parsed["label"], "reason": "gemini_ok"}

        print("[Gemini Parse Error]", content)
        return {"label": None, "reason": "gemini_parse_failed"}

    except requests.exceptions.RequestException as e:
        print(f"[Gemini Exception] {type(e).__name__}: {e}")
        return {"label": None, "reason": f"gemini_error:{type(e).__name__}"}
    except Exception as e:
        print(f"[Gemini Unknown Error] {e}")
        return {"label": None, "reason": f"gemini_error:{type(e).__name__}"}
