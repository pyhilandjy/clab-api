import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import audio, reports, stt, users
from app.services.audio import download_and_process_file

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler(timezone=f"Asia/Seoul")
    scheduler.add_job(func=download_and_process_file, trigger="interval", minutes=10)
    scheduler.start()
    yield


# FastAPI 앱 생성
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(audio.router, prefix="/audio")
app.include_router(users.router)
# app.include_router(files.router, prefix="/files")
app.include_router(stt.router, prefix="/stt")
app.include_router(reports.router)

# depends api key
# app.include_router(audio.router, prefix="/audio", dependencies=[Depends(get_api_key)])
# app.include_router(users.router, prefix="/users", dependencies=[Depends(get_api_key)])
# app.include_router(files.router, prefix="/files", dependencies=[Depends(get_api_key)])
# app.include_router(stt.router, prefix="/stt", dependencies=[Depends(get_api_key)])


@app.get("/")
async def home():
    return {"status": "ok"}
