from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.services.management import (
    get_audio_info,
    get_reports_with_pagination,
    select_reports_audio_files,
    update_audio_file_is_used,
    update_user_reports_inspection,
    update_user_reports_inspector,
    update_user_missions_is_open,
)

router = APIRouter()


@router.get("/management/reports/list", tags=["Management"])
async def get_user_reports(
    page: int = Query(..., ge=1), page_size: int = Query(..., ge=1, le=100)
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


class UpdateUserReportsInspection(BaseModel):
    inspection: str


@router.patch(
    "/management/user/reports/inspection/{user_reports_id}", tags=["Management"]
)
async def patch_user_reports_inspection(
    user_reports_id: str, payload: UpdateUserReportsInspection
):
    """
    user_reports_id 별 inspection 업데이트
    """
    update_user_reports_inspection(user_reports_id, payload.inspection)
    return {"message": "success"}


class UpdateUserReportsInspector(BaseModel):
    inspector: str


@router.patch(
    "/management/user/reports/inspector/{user_reports_id}", tags=["Management"]
)
async def patch_user_reports_inspection(
    user_reports_id: str, payload: UpdateUserReportsInspector
):
    """
    user_reports_id 별 inspector 업데이트
    """
    update_user_reports_inspector(user_reports_id, payload.inspector)
    return {"message": "success"}


@router.get("/stt/audio-info/{audio_files_id}", tags=["STT"])
async def get_audio_infos(audio_files_id: str):
    return get_audio_info(audio_files_id)

@router.get("/test", tags=["Test"])
def test(user_reports_id: str):
    return update_user_missions_is_open(user_reports_id)