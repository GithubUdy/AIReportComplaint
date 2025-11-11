
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import ml, reports
from .auth import router as auth_router
from .services import model as _model

app = FastAPI(title="AI Complaint System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

@app.on_event("startup")
def _warmup():
    try:
        _model.load_model()
        print("model warmed up")
    except Exception as e:
        print("model warmup failed:", e)

app.include_router(auth_router)
app.include_router(ml.router)
app.include_router(reports.router)

@app.get("/health")
def health():
    return {"status":"ok"}
