import os

from datetime import date
from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from pydantic import BaseModel

from app.services.report import (
    create_morphs_data,
    create_wordcoud,
    create_violinplot,
    create_report_data,
    select_act_count,
)

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


@router.post("/wordcloud/", tags=["Report"])
async def generate_wordcloud(report_model: ReportModle):
    """워드클라우드를 생성하여 이미지패스를 반환하는 엔드포인트"""
    image_path = create_wordcoud(**report_model.model_dump())
    return image_path


@router.post("/violinplot/", tags=["Report"])
async def generate_violinplot(report_model: ReportModle):
    """바이올린플롯를 생성하여 이미지 반환하는 엔드포인트"""
    image_path = create_violinplot(**report_model.model_dump())
    return FileResponse(image_path)


@router.get("/images/{image_path}", response_class=FileResponse, tags=["Report"])
def get_image(image_path: str):
    """이미지를 제공하는 엔드포인트"""
    file_path = os.path.join("./app/image/", image_path)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(file_path)


@router.post("/data/", tags=["Report"])
async def morphs(report_model: ReportModle):
    """문장길이, 녹음시간 반환 앤드포인트"""
    report_data = create_report_data(**report_model.model_dump())
    return report_data


@router.post("/act_count/", tags=["Report"])
async def act_count(report_model: ReportModle):
    """화행 갯수 반환 앤드포인트"""
    act_count_data = select_act_count(**report_model.model_dump())
    return act_count_data
