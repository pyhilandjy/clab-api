import os
import io
import pandas as pd

from datetime import date
from typing import List

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, BackgroundTasks
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
    create_file_path,
    gen_report_file_metadata,
    insert_report_metadata,
    update_report_id,
    save_report_file_s3,
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


@router.post("/csv/", tags=["Report"])
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

        merged_df["녹음기간"] = report_date_data["녹음기간"]
        merged_df["녹음시간"] = record_time_data["녹음시간"]

        sentence_len_cols = df_sentence_len.columns.tolist()
        morps_data_cols = df_morphs.columns.tolist()
        act_count_data_cols = df_act_count.columns.tolist()

        desired_columns_order = (
            ["녹음기간", "녹음시간"]
            + sentence_len_cols
            + morps_data_cols
            + act_count_data_cols
        )
        merged_df = merged_df[desired_columns_order]

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            merged_df.to_excel(writer, index=True, sheet_name="Report")
        output.seek(0)

        headers = {"Content-Disposition": 'attachment; filename="report.xlsx"'}
        return StreamingResponse(
            output,
            headers=headers,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class ReportFileModel(BaseModel):
    file: UploadFile = File(...)
    user_id: str
    start_date: date
    end_date: date


@router.post("/upload/pdf/", tags=["Report"])
async def upload_report_pdf(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    start_date: date = Form(...),
    end_date: date = Form(...),
):
    try:
        title = file.filename[:-4]
        file_path = create_file_path(user_id, title)
        metadata = gen_report_file_metadata(user_id, title, file_path)
        id = insert_report_metadata(metadata)
        update_report_id(id, user_id, start_date, end_date)
        save_report_file_s3(file, file_path)
        return {"message": id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pdf/", tags=["Report"])
async def select_report_pdf(report_model: ReportModel):
    pass
