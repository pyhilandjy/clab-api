import io
import os
import zipfile
from datetime import date
from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from app.db.query import (SELECT_IMAGE_FILES, SELECT_IMAGE_TYPE,
                          SELECT_STT_RESULTS_FOR_IMAGE)
from app.db.worker import execute_select_query
from app.services.report import (FONT_PATH, create_wordcloud,
                                 fetch_image_from_s3, violin_chart)

router = APIRouter()


class ImageModel(BaseModel):
    user_id: str
    start_date: date
    end_date: date


@router.post("/create/wordcloud/", tags=["image"])
async def generate_wordcloud(image_model: ImageModel):
    """워드클라우드를 생성하여 이미지 반환하는 엔드포인트"""
    stt_wordcloud = execute_select_query(
        query=SELECT_STT_RESULTS_FOR_IMAGE,
        params={
            "user_id": image_model.user_id,
            "start_date": image_model.start_date,
            "end_date": image_model.end_date,
        },
    )

    if not stt_wordcloud:
        raise HTTPException(
            status_code=404,
            detail="No STT results found for the specified user and date range.",
        )

    font_path = FONT_PATH

    # 워드클라우드 생성 및 이미지 저장
    type = "wordcloud"
    response, local_image_paths = create_wordcloud(
        stt_wordcloud, font_path, type, **dict(image_model)
    )
    if "error" in response:
        raise HTTPException(status_code=500, detail=response["error"])

    return {"local_image_paths": local_image_paths}


@router.get("/images/{image_path}", response_class=FileResponse, tags=["image"])
def get_image(image_path: str):
    """이미지를 제공하는 엔드포인트"""
    file_path = os.path.join("./app/image/", image_path)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(file_path)


class Imagefile(BaseModel):
    user_id: str
    start_date: date
    end_date: date
    type: str


@router.post("/image_files/images/", tags=["image"])
async def get_images(imagefilemodel: Imagefile):
    """
    images를 zip파일로 반환하는 엔드포인트
    """

    image_files_path = execute_select_query(
        query=SELECT_IMAGE_FILES,
        params={
            "user_id": imagefilemodel.user_id,
            "start_date": imagefilemodel.start_date,
            "end_date": imagefilemodel.end_date,
            "type": imagefilemodel.type,
        },
    )

    if not image_files_path:
        raise HTTPException(status_code=404, detail="files not found")
    bucket_name = "connectslab"
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for item in image_files_path:
            object_key = item["image_path"]
            image_data = fetch_image_from_s3(bucket_name, object_key)
            zip_file.writestr(os.path.basename(object_key), image_data)

    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={image_files_path}_images.zip"
        },
    )


class Imagetype(BaseModel):
    user_id: str
    start_date: date
    end_date: date


@router.post("/image_files/image_type/", tags=["image"], response_model=List[dict])
async def get_image_type(imagetypemodel: Imagetype):
    """
    user_id, start_date, end_date 별로 image_type을 가져오는 엔드포인트
    """

    image_type = execute_select_query(
        query=SELECT_IMAGE_TYPE,
        params={
            "user_id": imagetypemodel.user_id,
            "start_date": imagetypemodel.start_date,
            "end_date": imagetypemodel.end_date,
        },
    )

    if not image_type:
        raise HTTPException(status_code=404, detail="type not found")

    return image_type


@router.post("/create/violinplot/", tags=["image"])
async def generate_violin_chart(image_model: ImageModel):
    """워드클라우드를 생성하여 이미지 반환하는 엔드포인트(현재 2개의 파일은 보여지는것 구현x)"""
    stt_violin_chart = execute_select_query(
        query=SELECT_STT_RESULTS_FOR_IMAGE,
        params={
            "user_id": image_model.user_id,
            "start_date": image_model.start_date,
            "end_date": image_model.end_date,
        },
    )
    user_id = image_model.user_id
    start_date = image_model.start_date
    end_date = image_model.end_date
    type = "violin"
    font_path = FONT_PATH

    if not stt_violin_chart:
        raise HTTPException(
            status_code=404,
            detail="No STT results found for the specified user and date range.",
        )
    response = violin_chart(
        stt_violin_chart, user_id, start_date, end_date, type, font_path
    )
    if "error" in response:
        raise HTTPException(status_code=500, detail=response["error"])
    # 생성된 이미지를 직접 반환
    return FileResponse(response)
