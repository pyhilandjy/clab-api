import os
import io
import pandas as pd

from datetime import date
from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse

from pydantic import BaseModel

from app.services.report import (
    create_morphs_data,
    create_wordcoud,
    create_violinplot,
    create_sentence_len,
    select_act_count,
    create_audio_record_time,
    create_report_date,
)

router = APIRouter()


class ReportModel(BaseModel):
    user_id: str
    start_date: date
    end_date: date


@router.post("/wordcloud/", tags=["Report"])
async def generate_wordcloud(report_model: ReportModel):
    """워드클라우드를 생성하여 이미지패스를 반환하는 엔드포인트"""
    image_path = create_wordcoud(**report_model.model_dump())
    return image_path


@router.post("/violinplot/", tags=["Report"])
async def generate_violinplot(report_model: ReportModel):
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


@router.post(
    "/morphs-info/",
    tags=["Report"],
    response_model=dict,
)
async def create_morphs_info(report_model: ReportModel):
    """품사비율 반환 앤드포인트"""
    morps_data = create_morphs_data(**report_model.model_dump())
    if not morps_data:
        raise HTTPException(status_code=404, detail="STT result not found")
    return morps_data


@router.post("/sentence_len/", tags=["Report"])
async def sentence_len(report_model: ReportModel):
    """문장길이, 녹음시간 반환 앤드포인트"""
    sentence_len = create_sentence_len(**report_model.model_dump())
    return sentence_len


@router.post("/act-count/", tags=["Report"])
async def act_count(report_model: ReportModel):
    """화행 갯수 반환 앤드포인트"""
    act_count_data = select_act_count(**report_model.model_dump())
    return act_count_data


@router.post("/audio_record_time/", tags=["Report"])
async def record_time(report_model: ReportModel):
    """문장길이, 녹음시간 반환 앤드포인트"""
    audio_record_time = create_audio_record_time(**report_model.model_dump())
    return audio_record_time


@router.post("/generate-csv/", tags=["Report"])
async def generate_csv(report_model: ReportModel):
    try:
        morps_data = create_morphs_data(**report_model.model_dump())
        act_count_data = select_act_count(**report_model.model_dump())
        sentence_len = create_sentence_len(**report_model.model_dump())
        record_time_data = create_audio_record_time(**report_model.model_dump())
        report_date_data = create_report_date(**report_model.model_dump())

        df_morphs = pd.DataFrame(morps_data).T
        df_act_count = pd.DataFrame(act_count_data).T
        df_sentence_len = pd.DataFrame(sentence_len).T

        merged_df = df_sentence_len.join(
            df_act_count, lsuffix="_sentence", rsuffix="_act"
        )
        merged_df = merged_df.join(df_morphs, lsuffix="_merged", rsuffix="_morphs")

        # Add the record_time_data and report_date_data to each row
        merged_df["녹음시간"] = record_time_data["녹음시간"]
        merged_df["녹음기간"] = report_date_data["녹음기간"]

        # Move the "녹음기간" and "보고기간" columns to the front
        columns = ["녹음기간", "녹음시간"] + [
            col for col in merged_df.columns if col not in ["녹음시간", "녹음기간"]
        ]
        merged_df = merged_df[columns]

        output = io.StringIO()
        merged_df.to_csv(output, index=True)
        output.seek(0)

        headers = {"Content-Disposition": 'attachment; filename="report.csv"'}
        return StreamingResponse(output, headers=headers, media_type="text/csv")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
