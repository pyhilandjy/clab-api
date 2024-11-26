from supabase import Client, create_client

from app.db.worker import execute_insert_update_query, execute_select_query
from app.services.users import fetch_user_names
from app.db.query import (
    SELECT_REPORTS_PAGINATED,
    SELECT_TOTAL_COUNT,
    SELECT_REPORTS_AUDIO_FILES,
    UPDATE_AUDIO_FILE_IS_USED,
)
from app.config import settings
import datetime

supabase: Client = create_client(settings.supabase_url, settings.supabase_service_key)


async def get_reports_with_pagination(page: int, page_size: int):
    offset = (page - 1) * page_size

    reports = execute_select_query(
        query=SELECT_REPORTS_PAGINATED, params={"limit": page_size, "offset": offset}
    )
    reports = [dict(report) for report in reports]
    user_ids = [report["user_id"] for report in reports]
    user_data = await fetch_user_names(user_ids)

    for report in reports:
        user_id = report["user_id"]
        report["user_name"] = user_data.get(user_id, "")
        report["send_at"] = report["send_at"].strftime("%Y-%m-%d %H:%M:%S")

    total_count_result = execute_select_query(query=SELECT_TOTAL_COUNT, params={})
    total_count = total_count_result[0]["total_count"] if total_count_result else 0

    total_pages = (total_count + page_size - 1) // page_size

    return {
        "reports": reports,
        "total_count": total_count,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


def select_reports_audio_files(user_reports_id):
    datas = execute_select_query(
        query=SELECT_REPORTS_AUDIO_FILES,
        params={
            "user_reports_id": user_reports_id,
        },
    )
    datas = [dict(data) for data in datas]
    for d in datas:
        d["record_time"] = str(datetime.timedelta(seconds=d["record_time"]))
    return datas


def update_audio_file_is_used(audio_file_id: str, is_used: bool):
    execute_insert_update_query(
        query=UPDATE_AUDIO_FILE_IS_USED,
        params={"audio_file_id": audio_file_id, "is_used": is_used},
    )
