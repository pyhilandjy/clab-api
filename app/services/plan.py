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
)
from app.db.worker import execute_insert_update_query, execute_select_query
from app.error.utils import generate_error_response


def select_plans():
    return execute_select_query(query=SELECT_PLANS)


def select_plan(plan_id):
    return execute_select_query(
        query=SELECT_PLAN,
        params={
            "plan_id": plan_id,
        },
    )


def select_mission(plan_id):
    return execute_select_query(
        query=SELECT_MISSION,
        params={
            "plan_id": plan_id,
        },
    )


def delete_plan(plan_id):
    # 미션이 있는지 확인하는 쿼리 실행
    mission = execute_select_query(
        query=SELECT_MISSION,
        params={
            "plan_id": plan_id,
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
                "plan_id": plan_id,
            },
        )
        return generate_error_response("DELETE_SUCCESS")
    except Exception as e:
        return generate_error_response("DELETE_ERROR", str(e))


def insert_plans(payload: dict):
    return execute_insert_update_query(
        query=INSERT_PLANS,
        params={
            "plan_name": payload["plan_name"],
            "price": payload["price"],
            "day": payload["day"],
            "start_age_month": payload["start_age_month"],
            "end_age_month": payload["end_age_month"],
            "description": payload["description"],
        },
    )


def update_plans(payload: dict):
    return execute_insert_update_query(
        query=UPDATE_PLANS,
        params={
            "id": payload["id"],
            "plan_name": payload["plan_name"],
            "price": payload["price"],
            "day": payload["day"],
            "start_age_month": payload["start_age_month"],
            "end_age_month": payload["end_age_month"],
            "description": payload["description"],
        },
    )


def update_plan_status(playload: dict):
    return execute_insert_update_query(
        query=UPDATE_PLAN_STATUS,
        params={
            "id": playload["id"],
            "status": playload["status"],
        },
    )


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


def update_user_plan(user_id, plan_id):
    plan = execute_select_query(
        query=SELECT_PLAN,
        params={
            "plan_id": plan_id,
        },
    )
    day = plan[0].day
    start_at, end_at = plan_date(day)
    execute_insert_update_query(
        query=INSERT_USER_PLAN,
        params={
            "plan_id": plan_id,
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
