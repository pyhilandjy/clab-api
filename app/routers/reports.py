import io
import os
from datetime import date
from typing import List

import pandas as pd
from fastapi import APIRouter, File, Form, Header, HTTPException, UploadFile, Depends
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from app.services.report import (
    create_audio_record_time,
    create_file_path,
    create_morphs_data,
    create_report_date,
    create_sentence_len,
    create_tmp_file_path,
    create_violinplot,
    create_wordcoud,
    export_to_excel,
    gen_report_file_metadata,
    get_report,
    get_report_file_path,
    get_report_metadata,
    group_stt_data_by_file_name,
    insert_report_metadata,
    save_report_file_s3,
    select_act_count,
    select_audio_id_stt_data,
    select_talk_more_count,
    update_file_path,
    update_report_id,
)
from app.services.users import get_current_user

router = APIRouter()


class ReportModel(BaseModel):
    user_id: str
    start_date: date
    end_date: date


@router.post("/report/wordcloud/", tags=["Report"])
async def generate_wordcloud(report_model: ReportModel):
    """워드클라우드를 생성하여 이미지패스를 반환하는 엔드포인트"""
    image_path = create_wordcoud(**report_model.model_dump())
    return image_path


@router.post("/report/violinplot/", tags=["Report"])
async def generate_violinplot(report_model: ReportModel):
    """바이올린플롯를 생성하여 이미지 반환하는 엔드포인트"""
    image_path = create_violinplot(**report_model.model_dump())
    return FileResponse(image_path)


@router.get("/report/images/{image_path}", response_class=FileResponse, tags=["Report"])
def get_image(image_path: str):
    """이미지를 제공하는 엔드포인트"""
    file_path = os.path.join("./app/image/", image_path)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(file_path)


@router.post(
    "/report/morphs-info/",
    tags=["Report"],
    response_model=dict,
)
async def create_morphs_info(report_model: ReportModel):
    """품사비율 반환 앤드포인트"""
    morps_data = create_morphs_data(**report_model.model_dump())
    if not morps_data:
        raise HTTPException(status_code=404, detail="STT result not found")
    return morps_data


@router.post("/report/sentence_len/", tags=["Report"])
async def sentence_len(report_model: ReportModel):
    """문장길이, 녹음시간 반환 앤드포인트"""
    sentence_len = create_sentence_len(**report_model.model_dump())
    return sentence_len


@router.post("/report/act-count/", tags=["Report"])
async def act_count(report_model: ReportModel):
    """화행 갯수 반환 앤드포인트"""
    act_count_data = select_act_count(**report_model.model_dump())
    return act_count_data


@router.post("/report/talk-more-count/", tags=["Report"])
async def talk_more_count(report_model: ReportModel):
    """화행 갯수 반환 앤드포인트"""
    talk_more_count_data = select_talk_more_count(**report_model.model_dump())
    return talk_more_count_data


@router.post("/report/audio_record_time/", tags=["Report"])
async def record_time(report_model: ReportModel):
    """문장길이, 녹음시간 반환 앤드포인트"""
    audio_record_time = create_audio_record_time(**report_model.model_dump())
    return audio_record_time


@router.post("/report/csv/", tags=["Report"])
async def generate_csv(report_model: ReportModel):
    try:
        morps_data = create_morphs_data(**report_model.model_dump())
        act_count_data = select_act_count(**report_model.model_dump())
        sentence_len = create_sentence_len(**report_model.model_dump())
        record_time_data = create_audio_record_time(**report_model.model_dump())
        report_date_data = create_report_date(**report_model.model_dump())
        talk_more_count_data = select_talk_more_count(**report_model.model_dump())

        df_morphs = pd.DataFrame(morps_data).T
        df_act_count = pd.DataFrame(act_count_data).T
        df_talk_more_count = pd.DataFrame(talk_more_count_data).T
        df_sentence_len = pd.DataFrame(sentence_len).T

        merged_df = df_sentence_len.join(
            df_act_count, how="outer", lsuffix="_sentence", rsuffix="_act"
        )
        merged_df = merged_df.join(
            df_morphs, how="outer", lsuffix="_merged", rsuffix="_morphs"
        )
        merged_df = merged_df.join(df_talk_more_count, how="outer", rsuffix="_t")

        merged_df["녹음기간"] = report_date_data["녹음기간"]
        merged_df["녹음시간"] = record_time_data["녹음시간"]

        sentence_len_cols = df_sentence_len.columns.tolist()
        morps_data_cols = df_morphs.columns.tolist()
        act_count_data_cols = df_act_count.columns.tolist()
        talk_more_count_data_cols = [col for col in df_talk_more_count.columns.tolist()]

        desired_columns_order = (
            ["녹음기간", "녹음시간"]
            + sentence_len_cols
            + morps_data_cols
            + act_count_data_cols
            + talk_more_count_data_cols
        )

        final_columns = [
            col for col in desired_columns_order if col in merged_df.columns
        ]

        merged_df = merged_df[final_columns]

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


@router.post("/report/", tags=["Report"])
async def upload_report_pdf(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    start_date: date = Form(...),
    end_date: date = Form(...),
):
    try:
        title = file.filename[:-4]
        tmp_file_path = create_tmp_file_path(user_id)
        metadata = gen_report_file_metadata(user_id, title, tmp_file_path)
        id = insert_report_metadata(metadata)
        # file_path temp->report_id update
        file_path = create_file_path(user_id, id)
        update_file_path(id, file_path)
        update_report_id(id, user_id, start_date, end_date)
        save_report_file_s3(file, file_path)
        return {"message": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/reports/", tags=["Report"])
async def select_report_metadata(user_id: str):
    report_metadata = get_report_metadata(user_id)
    return report_metadata


@router.get("/reports/", tags=["Report"])
async def select_report_metadata(current_user=Depends(get_current_user)):
    user_id = current_user.get("sub")
    report_metadata = get_report_metadata(user_id)
    return report_metadata


@router.get("/reports/{report}/", tags=["Report"])
async def select_report_pdf(report: str):
    file_path = get_report_file_path(report)
    return get_report(file_path)


@router.post("/report/stt/data/between_date/", tags=["Report"])
async def get_data(report_model: ReportModel):
    """file_ids의 stt result를 가져오는 엔드포인트"""
    try:
        file_ids, stt_data = select_audio_id_stt_data(**report_model.dict())
        grouped_data = group_stt_data_by_file_name(file_ids, stt_data)
        output = export_to_excel(grouped_data)

        headers = {"Content-Disposition": 'attachment; filename="stt_results.xlsx"'}
        return StreamingResponse(
            output,
            headers=headers,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
