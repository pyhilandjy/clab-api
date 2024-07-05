from fastapi import (
    APIRouter,
    File,
    Form,
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


@router.post("/", tags=["Audio"])
async def create_upload_file(
    background_tasks: BackgroundTasks,
    authorization: str = Header(...),
    audio: UploadFile = File(...),
):
    try:
        token = authorization.split(" ")[1]
        payload = get_user_info_from_token(token)
        user_id = payload.get("sub")
        file_path = create_file_path(user_id)
        user_name = payload.get("user_metadata")["full_name"]
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
