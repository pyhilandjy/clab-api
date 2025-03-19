import datetime
from typing import Optional
from sqlalchemy import text

from supabase import Client, create_client

from app.config import settings
from app.db.query import (
    SELECT_AUDIO_INFO,
    SELECT_REPORTS_AUDIO_FILES,
    # SELECT_REPORTS_PAGINATED,
    SELECT_TOTAL_COUNT,
    UPDATE_AUDIO_FILE_IS_USED,
    UPDATE_USER_REPORTS_INSPECTION,
    UPDATE_USER_REPORTS_INSPECTOR,
)


from app.db.worker import execute_insert_update_query, execute_select_query
from app.services.users import fetch_user_names

supabase: Client = create_client(settings.supabase_url, settings.supabase_service_key)


def calculate_progress(statuses):
    total = len(statuses)
    completed = statuses.count("COMPLETED")
    progress = f"{completed}/{total}"
    return progress


async def get_reports_with_pagination(
    page: int,
    page_size: int,
    inspection_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
    plan_name_filter: Optional[str] = None,
):
    offset = (page - 1) * page_size
    where_clauses = []
    query_params = {
        "limit": page_size,
        "offset": offset,
    }

    if inspection_filter:
        where_clauses.append("user_reports.inspection = :inspection_filter")
        query_params["inspection_filter"] = inspection_filter

    if status_filter:
        where_clauses.append("user_reports.status = :status_filter")
        query_params["status_filter"] = status_filter

    if plan_name_filter:
        where_clauses.append("plans.plan_name = :plan_name_filter")
        query_params["plan_name_filter"] = plan_name_filter

    where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"

    sql_query = text(
        f"""
    SELECT DISTINCT ON (user_reports.id)
        user_reports.id AS user_reports_id,
        user_reports.user_id AS user_id,
        user_reports.send_at AS send_at,
        user_reports.inspection AS inspection,
        user_reports.inspector AS inspector,
        user_reports.inspected_at AS inspected_at,
        user_reports.status AS status,
        NULL AS user_name,
        user_children.first_name AS child_name,
        reports.title AS report_title,
        plans.plan_name AS plans_name,
        (SELECT ARRAY_AGG(user_missions.status)
         FROM user_missions
         WHERE user_missions.user_reports_id = user_reports.id) AS mission_statuses,
        (SELECT COUNT(audio_files.id)
         FROM user_missions
         JOIN audio_files ON audio_files.user_missions_id = user_missions.id
         WHERE user_missions.user_reports_id = user_reports.id) AS audio_file_count,
        (SELECT COALESCE(SUM(audio_files.record_time), 0)
         FROM user_missions
         JOIN audio_files ON audio_files.user_missions_id = user_missions.id
         WHERE user_missions.user_reports_id = user_reports.id) AS total_record_time
    FROM
        user_reports
    LEFT JOIN (
        SELECT DISTINCT ON (user_reports_id) *
        FROM user_missions
        ORDER BY user_reports_id, created_at DESC
    ) user_missions ON user_missions.user_reports_id = user_reports.id
    LEFT JOIN user_plans ON user_missions.user_plans_id = user_plans.id
    LEFT JOIN plans ON user_plans.plans_id = plans.id
    LEFT JOIN user_children ON user_plans.user_children_id = user_children.id
    LEFT JOIN reports ON user_reports.reports_id = reports.id
    WHERE {where_clause}
    ORDER BY user_reports.id, user_reports.send_at DESC
    LIMIT :limit OFFSET :offset
    """
    )

    # 보고서 데이터 가져오기
    reports = execute_select_query(query=sql_query, params=query_params)
    reports = [dict(report) for report in reports]
    user_ids = [report["user_id"] for report in reports]
    user_data = await fetch_user_names(user_ids)

    # mission_statuses -> mission_progress로 변환 및 기타 데이터 포맷팅
    for report in reports:
        user_id = report["user_id"]
        report["user_name"] = user_data.get(user_id, "")

        # 날짜 포맷팅
        if report["send_at"]:
            report["send_at"] = report["send_at"].strftime("%Y/%m/%d %H:%M")
        if report["inspected_at"]:
            report["inspected_at"] = report["inspected_at"].strftime("%Y/%m/%d %H:%M")
        if report["total_record_time"]:
            report["total_record_time"] = (
                f"{report['total_record_time'] // 60}:{report['total_record_time'] % 60:02}"
            )

        # mission_progress 계산 및 대체
        statuses = report.pop("mission_statuses", [])
        report["mission_progress"] = calculate_progress(statuses) if statuses else "0/0"

    # 총 보고서 수 계산
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
        if d["edited_at"]:
            d["edited_at"] = d["edited_at"].strftime("%Y/%m/%d %H:%M")
    return datas


def update_audio_file_is_used(audio_file_id: str, is_used: bool):
    execute_insert_update_query(
        query=UPDATE_AUDIO_FILE_IS_USED,
        params={"audio_file_id": audio_file_id, "is_used": is_used},
    )


# user_reports의 status도 COMPLETED로 업데이트
def update_user_reports_inspection(user_reports_id: str, inspection: str):
    inspected_at = datetime.datetime.now() if inspection == "COMPLETED" else None
    status = "COMPLETED" if inspection == "COMPLETED" else "IN_PROGRESS"
    execute_insert_update_query(
        query=UPDATE_USER_REPORTS_INSPECTION,
        params={
            "inspection": inspection,
            "inspected_at": inspected_at,
            "user_reports_id": user_reports_id,
            "status": status,
        },
    )
    # execute_insert_update_query(
    #     query=UPDATE_USER_MISSIONS_IS_OPEN,
    #     params={"user_reports_id": user_reports_id, "is_open": is_open},
    # )


# inspector를 업데이트할때 user_missions의 is_open값을 업데이트
def update_user_reports_inspector(user_reports_id: str, inspector: str):
    execute_insert_update_query(
        query=UPDATE_USER_REPORTS_INSPECTOR,
        params={"inspector": inspector, "user_reports_id": user_reports_id},
    )
    # update_user_missions_is_open(user_reports_id)


# # TODO 수정필요 !!!!! 오픈은 user side에서 처리함
# def update_user_missions_is_open(user_reports_id: str):
#     # reports_id를 가져오기
#     reports_id = execute_select_query(
#         query=USER_REPORT_REPORT_ID,
#         params={"user_reports_id": user_reports_id},
#     )

#     # reports_id와 연결된 day 데이터 가져오기
#     all_reports_id_day = execute_select_query(
#         query=USER_REPORT_REPORT,
#         params={"user_reports_id": user_reports_id},
#     )

#     # 모든 missions의 day와 id 데이터 가져오기
#     all_missions_id_day = execute_select_query(
#         query=USER_REPORT_MISSIONS,
#         params={"user_reports_id": user_reports_id},
#     )
#     user_plans_id = reports_id[0]["user_plans_id"]
#     # reports_id에 해당하는 day 값을 가져오기
#     current_day = next(
#         (
#             item["report_day"]
#             for item in all_reports_id_day
#             if item["report_id"] == reports_id[0]["reports_id"]
#         ),
#         None,
#     )

#     if current_day is None:
#         raise ValueError("Current day not found for the given reports_id")

#     # 다음으로 큰 day 값 찾기
#     sorted_days = sorted(item["report_day"] for item in all_reports_id_day)
#     next_day = next((day for day in sorted_days if day > current_day), None)

#     if next_day is None:
#         pass
#     else:
#         # current_day + 1부터 next_day까지 범위의 day를 포함하는 mission_id 추출
#         day_range = range(current_day + 1, next_day + 1)
#         missions_in_range = [
#             str(mission["mission_id"])
#             for mission in all_missions_id_day
#             if mission["day"] in day_range
#         ]

#         for missions_id in missions_in_range:
#             execute_insert_update_query(
#                 query=UPDATE_USER_MISSIONS_IS_OPEN,
#                 params={"user_plans_id": user_plans_id, "missions_id": missions_id},
#             )

import datetime


def get_audio_info(audio_files_id):
    results = execute_select_query(
        query=SELECT_AUDIO_INFO, params={"audio_files_id": audio_files_id}
    )
    if results:
        results = [dict(data) for data in results]

        for result in results:
            birth_date = result.get("birth_date")
            if birth_date:
                today = datetime.date.today()
                age_years = today.year - birth_date.year
                age_months = today.month - birth_date.month
                if age_months < 0:
                    age_years -= 1
                    age_months += 12
                if age_years == 0:
                    result["age"] = f"{age_months}개월"
                else:
                    result["age"] = f"{age_years}년 {age_months}개월"
            result["created_at"] = result["created_at"].strftime("%Y/%m/%d %H:%M")
            result["record_time"] = str(
                datetime.timedelta(seconds=result["record_time"])
            )
        return results
    else:
        return []
