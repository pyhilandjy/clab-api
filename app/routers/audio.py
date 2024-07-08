from fastapi import (
    APIRouter,
    File,
    Depends,
    Header,
    HTTPException,
    UploadFile,
    BackgroundTasks,
)
from pydantic import BaseModel
import asyncio
from app.services.audio import (
    create_file_name,
    create_file_path,
    delete_file,
    get_files_by_user_id,
    process_audio_metadata,
    process_stt,
    upload_to_s3,
    download_and_process_file,
)
from app.services.users import get_user_info_from_token

router = APIRouter()


async def get_current_user(authorization: str = Header(...)):
    try:
        token = authorization.split(" ")[1]
        payload = get_user_info_from_token(token)
        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/", tags=["Audio"])
async def create_upload_file(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    audio: UploadFile = File(...),
):
    try:
        user_id = current_user.get("sub")
        file_path = create_file_path(user_id)
        user_name = current_user.get("user_metadata")["full_name"]
        file_name = create_file_name(user_name)
        await upload_to_s3(audio, file_path[2:])
        # 백그라운드 테스크 add
        background_tasks.add_task(
            download_and_process_file, file_path, user_id, file_name
        )
        # local file 정리

        return {"message": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class FileModel(BaseModel):
    user_id: str


@router.get("/user/{user_id}/files", tags=["Files"])
async def get_files(user_id: str):
    """
    files 데이터를 가져오는 엔드포인트
    """
    file_ids = get_files_by_user_id(user_id)
    if not file_ids:
        raise HTTPException(status_code=404, detail="Files not found")
    return file_ids
