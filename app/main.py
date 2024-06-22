from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.query import SELECT_USERS
from app.db.worker import execute_select_query
from app.routers import audio, stt

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(audio.router, prefix="/audio")
# app.include_router(users.router, prefix="/users")
# app.include_router(files.router, prefix="/files")
app.include_router(stt.router, prefix="/stt")

# depends api key
# app.include_router(audio.router, prefix="/audio", dependencies=[Depends(get_api_key)])
# app.include_router(users.router, prefix="/users", dependencies=[Depends(get_api_key)])
# app.include_router(files.router, prefix="/files", dependencies=[Depends(get_api_key)])
# app.include_router(stt.router, prefix="/stt", dependencies=[Depends(get_api_key)])


@app.get("/users/", tags=["Files"])
async def get_users():
    user_ids = get_all_users()
    return user_ids


def get_all_users():
    return execute_select_query(query=SELECT_USERS)


@app.get("/")
async def home():
    return {"status": "ok"}
