from typing import List

from fastapi import APIRouter

from pydantic import BaseModel

from app.services.user_reports import (
    save_wordcloud_data,
    select_wordcloud_data,
    update_wordcloud_data,
    select_user_reports_info,
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




@router.patch("/wordcloud/data", tags=["User_Report"])
def patch_wordcloud_data(wordcloud_data, insight, user_reports_id):
    return update_wordcloud_data(wordcloud_data, insight, user_reports_id)


@router.get("/user_reports/info", tags=["User_Report"])
async def get_user_reports_info(user_reports_id: str):
    result = await select_user_reports_info(user_reports_id)
    return result[0]
