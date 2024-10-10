from datetime import datetime, timedelta
import pytz

from app.db.query import (
    SELECT_PLANS,
    SELECT_MISSION,
    DELETE_PLAN,
    INSERT_PLANS,
    UPDATE_PLANS,
    SELECT_PLAN,
    UPDATE_PLAN_STATUS,
    SELECT_PLANS_USER,
    INSERT_USER_PLAN,
    UPDATE_MISSION_STATUS,
    DELETE_MISSION,
    DELETE_MISSION_MESSAGE,
    SELECT_SUB_CATEGORY,
    SELECT_MAIN_CATEGORY,
    SELECT_ALL_CATEGORIES,
    INSERT_MISSION,
    UPDATE_MISSION,
    SELECT_REPORTS,
    DELETE_REPORT,
    UPDATE_REPORT,
    INSERT_REPORT,
)
from app.db.worker import execute_insert_update_query, execute_select_query
from app.error.utils import generate_error_response


def select_plans():
    return execute_select_query(query=SELECT_PLANS)


def select_plan(plans_id):
    results = execute_select_query(
        query=SELECT_PLAN,
        params={
            "plans_id": plans_id,
        },
    )
    if results:
        plan = results[0]
        return plan
    return None


def select_mission(plans_id):
    return execute_select_query(
        query=SELECT_MISSION,
        params={
            "plans_id": plans_id,
        },
    )


def delete_plan(plans_id):
    # 미션이 있는지 확인하는 쿼리 실행
    mission = execute_select_query(
        query=SELECT_MISSION,
        params={
            "plans_id": plans_id,
        },
    )

    # 미션이 있을 경우 삭제 불가
    if mission:
        return generate_error_response("MISSION_EXISTS")

    # 미션이 없을 경우 계획 삭제
    try:
        execute_insert_update_query(
            query=DELETE_PLAN,
            params={
                "plans_id": plans_id,
            },
        )
        return generate_error_response("DELETE_SUCCESS")
    except Exception as e:
        return generate_error_response("DELETE_ERROR", str(e))


def insert_plans(payload: dict):
    return execute_insert_update_query(
        query=INSERT_PLANS,
        params={
            "plan_name": payload.get("plan_name"),
            "price": payload.get("price"),
            "day": payload.get("day"),
            "start_age_month": payload.get("start_age_month"),
            "end_age_month": payload.get("end_age_month"),
            "description": payload.get("description"),
            "type": payload.get("type"),
            "tags": payload.get("tags"),
            "category_id": payload.get("category_id"),
        },
    )


def update_plans(payload: dict):
    return execute_insert_update_query(
        query=UPDATE_PLANS,
        params={
            "id": payload.get("id"),
            "plan_name": payload.get("plan_name"),
            "price": payload.get("price"),
            "day": payload.get("day"),
            "start_age_month": payload.get("start_age_month"),
            "end_age_month": payload.get("end_age_month"),
            "description": payload.get("description"),
            "type": payload.get("type"),
            "tags": payload.get("tags"),
            "category_id": payload.get("category_id"),
        },
    )


def update_plan_status(plan_id, status):
    return execute_insert_update_query(
        query=UPDATE_PLAN_STATUS,
        params={
            "id": plan_id,
            "status": status,
        },
    )


def select_sub_category(parents_id):
    return execute_select_query(
        query=SELECT_SUB_CATEGORY, params={"parents_id": parents_id}
    )


def select_main_category():
    return execute_select_query(query=SELECT_MAIN_CATEGORY)


def get_all_categories():
    rows = execute_select_query(query=SELECT_ALL_CATEGORIES)

    categories = {}
    for row in rows:
        if row["parents_id"] is None:  # 메인 카테고리
            categories[row["id"]] = {
                "id": row["id"],
                "name": row["name"],
                "created_at": row["created_at"],
                "parents_id": None,
                "sub_categories": [],
            }
        else:  # 서브 카테고리
            if row["parents_id"] in categories:
                categories[row["parents_id"]]["sub_categories"].append(
                    {
                        "id": row["id"],
                        "name": row["name"],
                        "created_at": row["created_at"],
                        "parents_id": row["parents_id"],
                    }
                )

    return list(categories.values())


# user
def select_plans_user(user_id):
    return execute_select_query(
        query=SELECT_PLANS_USER,
        params={
            "user_id": user_id,
        },
    )


def plan_date(day: int):
    KST = pytz.timezone("Asia/Seoul")
    today = datetime.now(KST).date()

    # 오늘이 월요일이 아닌 경우 다음 주 월요일 설정
    if today.weekday() != 0:
        days_until_next_monday = (7 - today.weekday()) % 7
        start_at = today + timedelta(days=days_until_next_monday)
    else:
        start_at = today

    # 주말을 제외하고 day만큼 더하기
    end_at = start_at
    days_added = 0

    while days_added < day:
        end_at += timedelta(days=1)
        if end_at.weekday() < 5:
            days_added += 1

    return start_at, end_at


def update_user_plan(user_id, plans_id):
    plan = execute_select_query(
        query=SELECT_PLAN,
        params={
            "plans_id": plans_id,
        },
    )
    day = plan[0].day
    start_at, end_at = plan_date(day)
    execute_insert_update_query(
        query=INSERT_USER_PLAN,
        params={
            "plans_id": plans_id,
            "user_id": user_id,
            "start_at": start_at,
            "end_at": end_at,
        },
    )


def update_mission_status(playload: dict):
    return execute_insert_update_query(
        query=UPDATE_MISSION_STATUS,
        params={
            "id": playload["id"],
            "status": playload["status"],
        },
    )


def delete_mission(mission_id):
    execute_insert_update_query(
        query=DELETE_MISSION_MESSAGE,
        params={
            "mission_id": mission_id,
        },
    )

    execute_insert_update_query(
        query=DELETE_MISSION,
        params={
            "mission_id": mission_id,
        },
    )


def insert_mission(payload: dict):
    return execute_insert_update_query(
        query=INSERT_MISSION,
        params={
            "plans_id": payload["plans_id"],
            "title": payload["title"],
            "day": payload["day"],
            "message": payload["message"],
            "summation": payload["summation"],
        },
    )


def update_mission(payload: dict):
    return execute_insert_update_query(
        query=UPDATE_MISSION,
        params={
            "id": payload["id"],
            "title": payload["title"],
            "day": payload["day"],
            "message": payload["message"],
            "summation": payload["summation"],
        },
    )


def select_reports(plans_id):
    return execute_select_query(
        query=SELECT_REPORTS,
        params={
            "plans_id": plans_id,
        },
    )


def delete_report(report_id):
    return execute_insert_update_query(
        query=DELETE_REPORT,
        params={
            "report_id": report_id,
        },
    )


def update_report(report_data):
    return execute_insert_update_query(
        query=UPDATE_REPORT,
        params={
            "id": report_data["id"],
            "title": report_data["title"],
            "quant_analysis": report_data["quant_analysis"],
            "qual_analysis": report_data["qual_analysis"],
            "missions_id": report_data["missions_id"],
        },
    )


def insert_report(report_data):
    return execute_insert_update_query(
        query=INSERT_REPORT,
        params={
            "plans_id": report_data["plans_id"],
            "title": report_data["title"],
            "quant_analysis": report_data["quant_analysis"],
            "qual_analysis": report_data["qual_analysis"],
            "missions_id": report_data["missions_id"],
        },
    )
