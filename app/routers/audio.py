from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.services.audio import (
    create_audio_metadata,
    create_file_name,
    create_file_path,
    get_files_by_user_id,
    insert_audio_metadata,
    upload_to_s3,
    select_audio_file,
    select_audio_info,
)
from app.services.users import get_current_user

router = APIRouter()


@router.post("/", tags=["Audio"])
async def create_upload_file(
    current_user: dict = Depends(get_current_user),
    audio: UploadFile = File(...),
):
    try:
        user_id = current_user.get("sub")
        file_path = create_file_path(user_id)
        user_name = current_user.get("user_metadata")["full_name"]
        file_name = create_file_name(user_name)
        metadata = create_audio_metadata(user_id, file_name, file_path[2:])
        insert_audio_metadata(metadata)
        await upload_to_s3(audio, file_path[2:])

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


@router.get("/webm/{id}", tags=["Audio"])
async def get_audio_file(id: str, range: str = Header(None)):
    """file_id 별 audio_files 가져오는 앤드포인트"""
    return await select_audio_file(id, range)


@router.get("/webm/info/{id}", tags=["Audio"])
async def get_audio_info(id: str):
    """file_id 별 audio_files 정보 가져오는 앤드포인트"""
    record_time = await select_audio_info(id)
    return JSONResponse(content={"record_time": record_time})
