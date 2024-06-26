from fastapi import APIRouter, File, Form, HTTPException, UploadFile, BackgroundTasks
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
)

router = APIRouter()


async def process_and_cleanup(file_id: str, file_path: str):
    try:
        # process_stt와 upload_to_s3 작업을 병렬로 실행
        await asyncio.gather(process_stt(file_id, file_path), upload_to_s3(file_path))
        # 두 작업이 끝난 후 delete_file 실행
        await delete_file(file_path)
    except Exception as e:
        # 예외 처리 로직 (필요 시)
        raise e


@router.post("/upload/", tags=["Audio"])
async def create_upload_file(
    background_tasks: BackgroundTasks,
    user_id: str = Form(...),
    file: UploadFile = File(...),
):
    try:
        file_name = create_file_name(user_id)
        file_path = create_file_path(file_name)
        file_id = await process_audio_metadata(file, user_id, file_name, file_path)

        # 백그라운드 작업 추가
        background_tasks.add_task(process_and_cleanup, file_id, file_path)

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
