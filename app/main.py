import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware

from app.routers import audio, management, plan, report_files, stt, user_reports, users
from app.services.audio import download_and_process_file
from app.services.api_key import get_api_key

# 로깅 설정
log_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
log_file = "app.log"

# 파일 핸들러
file_handler = logging.handlers.TimedRotatingFileHandler(
    log_file, when="midnight", interval=1, backupCount=30
)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

# 콘솔 핸들러
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.INFO)

# 로거 설정 (기본 로거에 핸들러 등록)
logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler(timezone="Asia/Seoul")
    scheduler.add_job(func=download_and_process_file, trigger="interval", minutes=10)
    scheduler.start()
    yield


# FastAPI 앱 생성
app = FastAPI(lifespan=lifespan)


# HTTP 요청/응답 로깅 미들웨어 추가
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # 요청 시작 시 로그 기록
    logger.info(f"Request: {request.method} {request.url}")

    response = await call_next(request)

    # 응답 후 로그 기록
    logger.info(f"Response: {request.method} {request.url} - {response.status_code}")

    return response


# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://clab-admin.vercel.app",
        "https://clab-fe.vercel.app",
        "http://localhost:3001",
        "http://localhost:3100",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(audio.router, prefix="/audio")
app.include_router(users.router)
app.include_router(stt.router, prefix="/stt")
app.include_router(report_files.router)
app.include_router(plan.router)
app.include_router(management.router)
app.include_router(user_reports.router)

# API 키 의존성 적용 예 (현재는 주석 처리됨)
# app.include_router(audio.router, prefix="/audio", dependencies=[Depends(get_api_key)])
# app.include_router(users.router, dependencies=[Depends(get_api_key)])
# app.include_router(stt.router, prefix="/stt", dependencies=[Depends(get_api_key)])
# app.include_router(report_files.router, dependencies=[Depends(get_api_key)])
# app.include_router(plan.router, dependencies=[Depends(get_api_key)])
# app.include_router(management.router, dependencies=[Depends(get_api_key)])
# app.include_router(user_reports.router, dependencies=[Depends(get_api_key)])


@app.get("/")
async def home():
    return {"status": "ok"}
