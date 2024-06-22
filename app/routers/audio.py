from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

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

# 녹음페이지에서 오디오파일 업로드하면 백엔드로 전달함
# 백엔드에서 로컬 스토리지에 임시로 저장

# 클로바에 음성파일을 전달함
# 클로바로부터 결과값을 받아서 DB에 저장

# 음성파일 s3에 적재
# 로컬의 임시 음성파일 제거


@router.post("/upload/", tags=["Audio"])
async def create_upload_file(
    user_id: str = Form(...),
    file: UploadFile = File(...),
):
    try:
        file_name = create_file_name(user_id)
        file_path = create_file_path(file_name)
        file_id = await process_audio_metadata(file, user_id, file_name, file_path)
        await process_stt(file_id, file_path)
        await upload_to_s3(file_path)
        delete_file(file_path)

        return {"message": "success"}
    except Exception as e:
        raise e


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
