import logging
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import audio, report_files, stt, users, plan, management
from app.services.audio import download_and_process_file

# 로그 설정
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

# 로거 설정
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://clab-admin.vercel.app",
        "https://clab-fe.vercel.app",
        "http://localhost:3002",
        "http://localhost:3100",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(audio.router, prefix="/audio")
app.include_router(users.router)
app.include_router(stt.router, prefix="/stt")
app.include_router(report_files.router)
app.include_router(plan.router)
app.include_router(management.router)

# depends api key
# app.include_router(audio.router, prefix="/audio", dependencies=[Depends(get_api_key)])
# app.include_router(users.router, dependencies=[Depends(get_api_key)])
# app.include_router(stt.router, prefix="/stt", dependencies=[Depends(get_api_key)])
# app.include_router(reports.router, dependencies=[Depends(get_api_key)])


@app.get("/")
async def home():
    return {"status": "ok"}
