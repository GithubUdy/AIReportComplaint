import os, re, json, math
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, f1_score, classification_report
import joblib

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "dataset.csv"
MODEL_DIR = ROOT.parent / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

def clean(s:str)->str:
    s = re.sub(r"[^가-힣A-Za-z0-9\\s]", " ", s)
    s = re.sub(r"\\s+", " ", s)
    return s.strip()

df = pd.read_csv(DATA).dropna(subset=["text","label"])
df["text"] = df["text"].map(clean)
df = df[df["text"].str.len() > 0].reset_index(drop=True)

# --- 안전장치: 클래스별 최소 샘플 확보(≥2) ---
counts = df["label"].value_counts()
if (counts < 2).any():
    parts = []
    for lab, grp in df.groupby("label"):
        if len(grp) >= 2:
            parts.append(grp)
        else:
            # 1개밖에 없으면 동일 샘플 복제해서 최소 2개 맞춤
            parts.append(pd.concat([grp, grp], ignore_index=True))
    df = pd.concat(parts, ignore_index=True)
    counts = df["label"].value_counts()

# --- 동적 test_size: 테스트 샘플 수 ≥ 클래스 수 ---
n = len(df)
k = df["label"].nunique()
# 기본 0.2, 하지만 n*test_size >= k 가 되도록 상향
ts = max(0.2, (k + 0.5) / n)  # +0.5 여유
ts = min(ts, 0.5)             # 너무 커지지 않도록 상한

try:
    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["label"], test_size=ts, random_state=42, stratify=df["label"]
    )
except ValueError:
    # 여전히 불가능하면 stratify 없이 분할(소형 데이터 대응)
    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["label"], test_size=ts, random_state=42, stratify=None
    )

vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(2,5), min_df=1, sublinear_tf=True)
Xtr = vec.fit_transform(X_train)
clf = LinearSVC()
clf.fit(Xtr, y_train)

Xt = vec.transform(X_test)
pred = clf.predict(Xt)
acc = accuracy_score(y_test, pred)
f1m = f1_score(y_test, pred, average="macro")

print("Samples:", n, "Classes:", k, f"test_size={ts:.2f}")
print("ACC:", acc)
print("F1(macro):", f1m)
print(classification_report(y_test, pred))

joblib.dump(vec, MODEL_DIR / "tfidf.joblib")
joblib.dump(clf, MODEL_DIR / "svm.joblib")
with (MODEL_DIR / "metrics.json").open("w", encoding="utf-8") as f:
    json.dump({"accuracy": float(acc), "f1_macro": float(f1m)}, f, ensure_ascii=False, indent=2)

print("saved ->", MODEL_DIR)
