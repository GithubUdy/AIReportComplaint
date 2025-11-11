
import os, joblib, numpy as np
from typing import Tuple
from .rules import DEPT_MAP, evidence_keywords

MODEL_DIR = os.getenv("MODEL_DIR", os.path.join(os.path.dirname(__file__),"..","..","models"))
VEC_PATH  = os.path.join(MODEL_DIR,"tfidf.joblib")
CLF_PATH  = os.path.join(MODEL_DIR,"svm.joblib")

_vec = None
_clf = None

def load_model():
    global _vec, _clf
    if _vec is None: _vec = joblib.load(VEC_PATH)
    if _clf is None: _clf = joblib.load(CLF_PATH)

def predict(text:str)->Tuple[str,float]:
    load_model()
    X = _vec.transform([text])
    df = _clf.decision_function(X)
    if df.ndim == 1:
        score = float(abs(df[0]))
        conf = 1/(1+np.exp(-score/2))
        label = _clf.classes_[1 if df[0]>0 else 0]
        return label, float(conf)
    i = int(df.argmax())
    row = df[0]
    ex = np.exp(row - row.max())
    probs = ex/ex.sum()
    return _clf.classes_[i], float(probs[i])

def label_to_department(label:str)->int:
    return DEPT_MAP.get(label, 4)

def make_evidence(text:str,label:str):
    return evidence_keywords(text,label)
