
from typing import Optional

KEY_RULES = [
    ("시설", ["전등","형광등","엘리베이터","콘센트","누수","파손","수리","창문","문","냉난방기","에어컨"]),
    ("환경", ["소음","냄새","악취","청결","미화","벌레","분리수거","흡연","온도"]),
    ("전산", ["와이파이","wifi","인터넷","프린터","로그인","계정","서버","포털","메일","pc","컴퓨터"]),
    ("기타", ["분실","불친절","문의","건의","민원","안내"]),
]

DEPT_MAP = {"시설":1,"환경":2,"전산":3,"기타":4}
#THRESHOLD = 0.50
THRESHOLD = 0.99

def apply_keyword_rules(text:str)->Optional[str]:
    t = text.lower()
    best, hits = None, 0
    for lab, kws in KEY_RULES:
        c = sum(1 for kw in kws if kw.lower() in t)
        if c > hits:
            best, hits = lab, c
    return best if hits>0 else None

def evidence_keywords(text:str, label:str)->list[str]:
    t = text.lower()
    for lab, kws in KEY_RULES:
        if lab == label:
            return [kw for kw in kws if kw.lower() in t][:5]
    return []
