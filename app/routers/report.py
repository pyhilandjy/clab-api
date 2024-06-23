from datetime import date
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.report import create_morphs_data

router = APIRouter()


class ReportModle(BaseModel):
    user_id: str
    start_date: date
    end_date: date


@router.post(
    "/morphs_info",
    tags=["Report"],
    response_model=dict,
)
async def create_morphs_info(report_model: ReportModle):
    """품사비율 반환 앤드포인트"""
    morps_data = create_morphs_data(**report_model.model_dump())
    if not morps_data:
        raise HTTPException(status_code=404, detail="STT result not found")
    return morps_data
