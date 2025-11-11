<# 
  AI-Report 프로젝트 환경 자동 세팅 스크립트
  사용법(프로젝트 루트에서):
    powershell -ExecutionPolicy Bypass -File .\setup_env.ps1 -Port 8081 -Host 127.0.0.1

  옵션:
    -Port <int>    : uvicorn 포트 (기본 8081)
    -Host <string> : uvicorn 호스트 (기본 127.0.0.1)
    -NoServer      : 서버 실행 없이 환경/마이그레이션만 수행



    ModuleNotFoundError: No module named 'jwt' → pip install pyjwt

No module named 'fastapi_mail' → pip install fastapi-mail

email-validator is not installed → pip install email-validator

alembic: command not found → & ".\.venv\Scripts\python.exe" -m alembic upgrade head

Google Drive 한글 경로여도 스크립트는 & "$venvPython" -m ... 형태로 실행하니 OK

포트 점유 에러 → -Port 8082 처럼 다른 포트 지정해서 실행
#>

param(
  [int]$Port = 8081,
  [string]$Host = "127.0.0.1",
  [switch]$NoServer
)

$ErrorActionPreference = "Stop"

function Write-Title($msg) { Write-Host "`n=== $msg ===" -ForegroundColor Cyan }
function Write-Ok($msg)    { Write-Host "✔ $msg" -ForegroundColor Green }
function Write-Warn($msg)  { Write-Host "⚠ $msg" -ForegroundColor Yellow }
function Write-Err($msg)   { Write-Host "✘ $msg" -ForegroundColor Red }

# 1) 현재 위치 확인
$projRoot = (Get-Location).Path
Write-Title "프로젝트 루트 확인"
Write-Host $projRoot

# 2) Python 존재 확인
Write-Title "Python 확인"
try {
  $pyVersion = & python --version 2>$null
  Write-Ok "Python 발견: $pyVersion"
} catch {
  Write-Err "python 명령을 찾을 수 없어요. https://www.python.org/ 에서 설치 후 다시 실행하세요."
  exit 1
}

# 3) venv 생성 및 경로
$venvDir = Join-Path $projRoot ".venv"
$venvPython = Join-Path $venvDir "Scripts\python.exe"

Write-Title "가상환경 점검"
if (!(Test-Path $venvPython)) {
  Write-Warn "가상환경(.venv)이 없어 생성합니다…"
  & python -m venv ".venv"
  Write-Ok "가상환경 생성 완료"
} else {
  Write-Ok "가상환경 발견"
}

# 4) pip 업그레이드
Write-Title "pip 업그레이드"
& "$venvPython" -m pip install --upgrade pip setuptools wheel
Write-Ok "pip/setuptools/wheel 업그레이드 완료"

# 5) 의존성 설치
Write-Title "requirements 설치"
$reqFile = Join-Path $projRoot "requirements.txt"
if (Test-Path $reqFile) {
  & "$venvPython" -m pip install -r "$reqFile"
  Write-Ok "requirements.txt 설치 완료"
} else {
  Write-Warn "requirements.txt가 없어 핵심 패키지만 설치합니다"
  & "$venvPython" -m pip install `
    fastapi==0.115.0 uvicorn==0.30.6 `
    SQLAlchemy==2.0.36 alembic==1.13.2 asyncmy==0.2.9 `
    pydantic==2.9.2 pydantic-settings==2.6.1 `
    PyJWT==2.9.0 passlib[bcrypt]==1.7.4 `
    fastapi-mail==1.4.1 python-multipart==0.0.9 `
    watchfiles==0.23.0 email-validator==2.2.0 `
    aioredis==2.0.1 redis==5.1.1
  Write-Ok "핵심 패키지 설치 완료"
}

# 6) .env 구성
Write-Title ".env 구성"
$envFile = Join-Path $projRoot ".env"
$exampleFile = Join-Path $projRoot ".env.example"

if (!(Test-Path $envFile)) {
  if (Test-Path $exampleFile) {
    Copy-Item $exampleFile $envFile
    Write-Ok ".env.example을 .env로 복사함"
  } else {
    Write-Warn ".env.example이 없어 최소 템플릿 .env를 생성합니다"
    @"
# --- Core ---
APP_NAME=AI Report Backend
APP_ENV=dev
HOST=$Host
PORT=$Port

# --- Security ---
JWT_SECRET=dev-super-secret-please-change
JWT_ALG=HS256
ACCESS_EXPIRES=28800

# --- DB (MySQL 예시) ---
DB_URI=mysql+asyncmy://user:password@localhost:3306/ai_report

# --- Mail ---
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_FROM=
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_FROM_NAME=Campus Report System
MAIL_TLS=True
MAIL_SSL=False

# --- Storage ---
FILES_DIR=./data/files

# --- Redis (선택) ---
REDIS_URL=redis://localhost:6379/0
"@ | Out-File -Encoding UTF8 $envFile
    Write-Ok "기본 .env 템플릿 생성"
  }
} else {
  Write-Ok ".env 이미 존재"
}

# 7) Alembic 마이그레이션
Write-Title "DB 마이그레이션 (alembic upgrade head)"
$alembicIni = Join-Path $projRoot "alembic.ini"
if (!(Test-Path $alembicIni)) {
  # 프로젝트 구조가 app/db/migrations인 경우도 대응
  $altIni = Join-Path $projRoot "app\db\migrations\alembic.ini"
  if (Test-Path $altIni) { $alembicIni = $altIni }
}

if (Test-Path $alembicIni) {
  try {
    & "$venvPython" -m alembic upgrade head
    Write-Ok "alembic upgrade head 완료"
  } catch {
    Write-Warn "alembic 실행 실패. alembic.ini 위치/설정 확인 필요"
  }
} else {
  Write-Warn "alembic.ini를 찾지 못해 마이그레이션을 건너뜁니다"
}

# 8) 필수 모듈 로딩 체크 (실패 시 즉시 재설치 안내)
Write-Title "핵심 모듈 임포트 체크"
$imports = @("fastapi","uvicorn","jwt","fastapi_mail","sqlalchemy","pydantic","email_validator")
$missing = @()
foreach ($m in $imports) {
  try {
    & "$venvPython" - <<PY
import $m
print("$m: OK")
PY
  } catch {
    $missing += $m
  }
}
if ($missing.Count -gt 0) {
  Write-Warn "다음 모듈 임포트 실패: $($missing -join ', ')"
  Write-Host "재설치 시도…" -ForegroundColor Yellow
  & "$venvPython" -m pip install $missing
} else {
  Write-Ok "핵심 모듈 임포트 OK"
}

# 9) 서버 실행 (옵션)
if (-not $NoServer) {
  Write-Title "UVICORN 서버 실행"
  Write-Host "URL: http://$Host:$Port/docs" -ForegroundColor Cyan
  # 비 ASCII 경로 대응 위해 & "…python.exe" -m module 형식 사용
  & "$venvPython" -m uvicorn app.main:app --reload --host $Host --port $Port
} else {
  Write-Ok "서버 실행은 생략(-NoServer)"
  Write-Host "수동 실행 명령:" -ForegroundColor Yellow
  Write-Host "`"$venvPython`" -m uvicorn app.main:app --reload --host $Host --port $Port"
}
