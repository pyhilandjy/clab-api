from typing import List, Dict
from fastapi import APIRouter

from pydantic import BaseModel

from app.services.user_reports import (
    save_wordcloud_data,
    select_wordcloud_data,
    update_wordcloud_data,
    select_user_reports_info,
    save_sentence_length_data,
    select_sentence_length_data,
    save_pos_ratio_data,
    update_sentence_length_data,
    update_pos_ratio_data,
    save_speech_act_data,
    select_insight_data,
    upsert_insight_data,
    update_speech_act_data,
    select_cover_data,
    delete_reports_data,
    generate_reports_data,
)

router = APIRouter()


@router.get("/cover/data", tags=["User_Report"])
def get_cover_data(user_reports_id: str):
    return select_cover_data(user_reports_id)


class UserReportsId(BaseModel):
    user_reports_id: str


@router.post("/wordcloud/data", tags=["User_Report"])
def kiwi_nouns_count(user_reports_id: UserReportsId):
    data = user_reports_id.model_dump()
    user_reports_id = data["user_reports_id"]
    return save_wordcloud_data(user_reports_id)


@router.get("/wordcloud/data", tags=["User_Report"])
def get_wordcloud_data(user_reports_id):
    return select_wordcloud_data(user_reports_id)


# class WordCounts(BaseModel):
#     # [word: string]: number 형식을 Dict[str, int]로 표현
#     __root__: Dict[str, int]


class WordcloudSpeakerData(BaseModel):
    speaker: str
    word_counts: Dict[str, int]


class WordcloudData(BaseModel):
    data: List[WordcloudSpeakerData]
    insights: str


class WordcloudUpdateRequest(BaseModel):
    user_reports_id: str
    wordcloud_data: WordcloudData


@router.patch("/wordcloud/data", tags=["User_Report"])
async def patch_wordcloud_data(request: WordcloudUpdateRequest):
    data = request.model_dump()
    user_reports_id = data["user_reports_id"]
    wordcloud_data = data["wordcloud_data"]
    return update_wordcloud_data(wordcloud_data, user_reports_id)


@router.get("/user_reports/info", tags=["User_Report"])
async def get_user_reports_info(user_reports_id: str):
    result = await select_user_reports_info(user_reports_id)
    return result[0]


# violinplot
@router.post("/sentence_length/data", tags=["User_Report"])
def create_sentence_length_data(user_reports_id: UserReportsId):
    data = user_reports_id.model_dump()
    user_reports_id = data["user_reports_id"]
    return save_sentence_length_data(user_reports_id)


@router.get("/sentence_length/data", tags=["User_Report"])
def get_sentence_length_data(user_reports_id):
    return select_sentence_length_data(user_reports_id)


class SentenceLengthData(BaseModel):
    data: List
    insights: str


class SentenceLengthUpdateRequest(BaseModel):
    user_reports_id: str
    sentence_length_data: SentenceLengthData


@router.patch("/sentence_length/data", tags=["User_Report"])
async def patch_sentence_length_data(request: SentenceLengthUpdateRequest):
    data = request.model_dump()
    user_reports_id = data["user_reports_id"]
    sentence_length_data = data["sentence_length_data"]
    return update_sentence_length_data(sentence_length_data, user_reports_id)


# tokenize
@router.post("/pos_ratio/data", tags=["User_Report"])
def create_pos_ratio_data(user_reports_id: UserReportsId):
    data = user_reports_id.model_dump()
    user_reports_id = data["user_reports_id"]
    return save_pos_ratio_data(user_reports_id)


class POSRatioSpeakerData(BaseModel):
    speaker: str
    pos_ratio_data: Dict[str, int]


class POSRatioData(BaseModel):
    data: List[POSRatioSpeakerData]
    insights: str


class POSRatioUpdateRequest(BaseModel):
    user_reports_id: str
    pos_ratio_data: POSRatioData


@router.patch("/pos_ratio/data", tags=["User_Report"])
def patch_pos_ratio_data(request: POSRatioUpdateRequest):
    data = request.model_dump()
    user_reports_id = data["user_reports_id"]
    pos_ratio_data = data["pos_ratio_data"]
    return update_pos_ratio_data(user_reports_id, pos_ratio_data)


# speech acts
@router.post("/speech_act/data", tags=["User_Report"])
def create_speech_act_data(user_reports_id: UserReportsId):
    data = user_reports_id.model_dump()
    user_reports_id = data["user_reports_id"]
    return save_speech_act_data(user_reports_id)


class SpeechActSpeakerData(BaseModel):
    speaker: str
    speech_act: List[Dict[str, Dict[str, int]]]


class SpeechActData(BaseModel):
    data: List[SpeechActSpeakerData]
    insights: str = None


class SpeechActUpdateRequest(BaseModel):
    user_reports_id: str
    speech_act_data: SpeechActData


@router.patch("/speech_act/data", tags=["User_Report"])
def patch_speech_act_data(request: SpeechActUpdateRequest):
    data = request.model_dump()
    user_reports_id = data["user_reports_id"]
    speech_act_data = data["speech_act_data"]
    return update_speech_act_data(user_reports_id, speech_act_data)


# insight


@router.get("/insight/data", tags=["User_Report"])
def get_insight_data(user_reports_id: str):
    return select_insight_data(user_reports_id)


class InsightData(BaseModel):
    id: str = None
    user_reports_id: str
    reports_order: int
    title: str = None
    text: List[str] = []
    insight: str = None
    example: str = None
    created_at: str = None


@router.put("/insight/data", tags=["User_Report"])
def put_insight_data(insight_data: InsightData):
    data = insight_data.model_dump()
    # 빈 문자열을 None으로 변환
    for key, value in data.items():
        if value == "":
            data[key] = None

    insight_id = upsert_insight_data(data)
    return insight_id


from fastapi import HTTPException


class UserReportsId(BaseModel):
    user_reports_id: str


@router.post("/reports/regenerate/{user_reports_id}", tags=["User_Report"])
async def regenerate_reports_data(user_reports_id: str):
    try:

        delete_reports_data(user_reports_id)
        generate_reports_data(user_reports_id)

        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
