from typing import List

from fastapi import APIRouter

from app.services.user_reports import (
    save_wordcloud_data,
    select_wordcloud_data,
    update_wordcloud_data,
)

router = APIRouter()


@router.post("/wordcloud/data", tags=["User_Report"])
def kiwi_nouns_count(user_reports_id: str):
    return save_wordcloud_data(user_reports_id)


@router.get("/wordcloud/data", tags=["User_Report"])
def get_wordcloud_data(user_reports_id):
    return select_wordcloud_data(user_reports_id)


@router.patch("/wordcloud/data", tags=["User_Report"])
def patch_wordcloud_data(wordcloud_data, user_reports_id):
    return update_wordcloud_data(wordcloud_data, user_reports_id)
