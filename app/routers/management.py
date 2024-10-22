from fastapi import APIRouter
from pydantic import BaseModel

import datetime

from app.services.management import select_user_reports

router = APIRouter()


class UserReport(BaseModel):
    id: str
    user_id: str
    reports_id: str
    sand_at: datetime
    status: str
    file_path: str


@router.get("/user/reports", tags=["Management"])
async def get_user_reports():
    """
    user_reports 데이터를 가져오는 엔드포인트
    """
    select_user_reports()
