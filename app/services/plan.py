from app.db.query import (
    SELECT_PLANS,
    SELECT_MISSION,
    DELETE_PLAN,
    INSERT_PLANS,
    UPDATE_PLANS,
    SELECT_PLAN,
    UPDATE_PLAN_STATUS,
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
