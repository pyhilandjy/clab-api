from fastapi import APIRouter, Query
from pydantic import BaseModel
from app.services.management import (
    get_reports_with_pagination,
    select_reports_audio_files,
    update_audio_file_is_used,
)

router = APIRouter()


@router.get("/management/reports/list", tags=["Management"])
async def get_user_reports(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)
):
    """
    user_reports 데이터를 가져오는 엔드포인트
    """
    result = await get_reports_with_pagination(page=page, page_size=page_size)
    return result


@router.get("/management/reports/audio_files/{user_reports_id}", tags=["Management"])
async def get_reports_audio_files(user_reports_id: str):
    """
    user_reports_id 별 audio_files 데이터를 가져오는 엔드포인트
    """
    audio_files = select_reports_audio_files(user_reports_id)
    if not audio_files:
        return []
    return audio_files


class UpdateAudioFileIsUsedPayload(BaseModel):
    is_used: bool


@router.patch("/management/reports/audio_files/{audio_file_id}", tags=["Management"])
async def patch_audio_file_is_used(
    audio_file_id: str, payload: UpdateAudioFileIsUsedPayload
):
    """
    audio_file_id 별 is_used 업데이트
    """
    update_audio_file_is_used(audio_file_id, payload.is_used)
    return {"message": "success"}
