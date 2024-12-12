from typing import List, Dict
import json
from fastapi import APIRouter

from pydantic import BaseModel

from app.services.user_reports import (
    save_wordcloud_data,
    select_wordcloud_data,
    update_wordcloud_data,
    select_user_reports_info,
    save_sentence_length_data,
    select_sentence_length_data,
    save_tokenized_data,
)

router = APIRouter()

class WordcloudData(BaseModel):
    user_reports_id: str

@router.post("/wordcloud/data", tags=["User_Report"])
def kiwi_nouns_count(user_reports_id: WordcloudData):
    data = user_reports_id.model_dump()
    user_reports_id = data["user_reports_id"]
    return save_wordcloud_data(user_reports_id)


@router.get("/wordcloud/data", tags=["User_Report"])
def get_wordcloud_data(user_reports_id):
    return select_wordcloud_data(user_reports_id)


class WordCounts(BaseModel):
    # [word: string]: number 형식을 Dict[str, int]로 표현
    __root__: Dict[str, int]

class SpeakerData(BaseModel):
    speaker: str
    word_counts: Dict[str, int]  # WordCounts 타입

class WordcloudData(BaseModel):
    data: List[SpeakerData]
    insights: str

class WordcloudUpdateRequest(BaseModel):
    user_reports_id: str
    wordcloud_data: WordcloudData



@router.patch("/wordcloud/data", tags=["User_Report"])
async def patch_wordcloud_data(request: WordcloudUpdateRequest):
    data = request.model_dump()
    user_reports_id = data["user_reports_id"]
    wordcloud_data = data["wordcloud_data"]
    data = json.dumps(wordcloud_data)
    return update_wordcloud_data(data, user_reports_id)


@router.get("/user_reports/info", tags=["User_Report"])
async def get_user_reports_info(user_reports_id: str):
    result = await select_user_reports_info(user_reports_id)
    return result[0]

#violinplot
@router.post("/sentence_length/data", tags=["User_Report"])
def create_sentence_length_data(user_reports_id: WordcloudData):
    data = user_reports_id.model_dump()
    user_reports_id = data["user_reports_id"]
    return save_sentence_length_data(user_reports_id)

@router.get("/sentence_length/data", tags=["User_Report"])
def get_sentence_length_data(user_reports_id):
    return select_sentence_length_data(user_reports_id)

#tokenize
@router.post("/tokenize/data", tags=["User_Report"])
def create_tokenized_data(user_reports_id: WordcloudData):
    data = user_reports_id.model_dump()
    user_reports_id = data["user_reports_id"]
    return save_tokenized_data(user_reports_id)