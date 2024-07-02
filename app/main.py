from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.query import SELECT_USERS
from app.db.worker import execute_select_query
from app.routers import audio, reports, stt, users
from app.services.api_key import get_api_key
import requests
from app.config import settings

app = FastAPI()


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
