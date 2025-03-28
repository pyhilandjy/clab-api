from datetime import datetime, timedelta
import uuid

import pytz
from supabase import create_client

from app.config import settings
from app.db.query import (
    DELETE_MISSION,
    DELETE_MISSION_MESSAGE,
    DELETE_PLAN,
    DELETE_REPORT,
    DELETE_REPORTS_ID_MISSIONS,
    INSERT_MISSION,
    INSERT_PLANS,
    INSERT_REPORT,
    INSERT_USER_PLAN,
    SELECT_ALL_CATEGORIES,
    SELECT_MAIN_CATEGORY,
    SELECT_MISSION,
    SELECT_MISSIONS_TITLE,
    SELECT_PLAN,
    SELECT_PLANS,
    SELECT_PLANS_USER,
    SELECT_REPORTS,
    SELECT_SUB_CATEGORY,
    UPDATE_MISSION,
    UPDATE_MISSION_STATUS,
    UPDATE_PLAN_STATUS,
    UPDATE_PLANS,
    UPDATE_REPORT,
    UPDATE_REPORTS_ID_MISSIONS,
    UPDATE_PLAN_DESCRIPTION_IMAGE,
    UPDATE_PLAN_SCHEDULE_IMAGE,
    UPDATE_PLAN_THUMBNAIL_IMAGE,
)
from app.db.worker import execute_insert_update_query, execute_select_query
from app.error.utils import generate_error_response

supabase = create_client(settings.supabase_url, settings.supabase_service_key)


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
        plan = dict(results[0])

        image_fields = [
            "description_image_id",
            "schedule_image_id",
            "thumbnail_image_id",
        ]

        for field in image_fields:
            try:
                if plan.get(field):
                    plan[f"{field}_url"] = supabase.storage.from_(
                        "plan-images"
                    ).get_public_url(plan[field])
                else:
                    plan[f"{field}_url"] = None
            except Exception as e:
                plan[f"{field}_url"] = None

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
    reports = execute_select_query(
        query=SELECT_REPORTS,
        params={
            "plans_id": plans_id,
        },
    )

    # 미션이 있을 경우 삭제 불가
    if mission or reports:
        return generate_error_response("MISSION_EXISTS")

    # 미션이 없을 경우 계획 삭제
    try:
        execute_insert_update_query(
            query=DELETE_PLAN,
            params={
                "plans_id": plans_id,
            },
        )
        delete_plan_image(plans_id)
        return generate_error_response("DELETE_SUCCESS")
    except Exception as e:
        return generate_error_response("DELETE_ERROR", str(e))


def delete_plan_image(plans_id):
    plan = execute_select_query(
        query=SELECT_PLAN,
        params={"plans_id": plans_id},
    )
    if plan:
        for field in [
            "description_image_id",
            "schedule_image_id",
            "thumbnail_image_id",
        ]:
            if plan[0].get(field):
                supabase.storage.from_("plan-images").remove(plan[0][field])


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
            "summary": payload.get("summary"),
            "schedule": payload.get("schedule"),
        },
        return_id=True,
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
            "summary": payload.get("summary"),
            "schedule": payload.get("schedule"),
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
            "summary": payload["summary"],
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
            "summary": payload["summary"],
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
            "wordcloud": report_data["wordcloud"],
            "sentence_length": report_data["sentence_length"],
            "pos_ratio": report_data["pos_ratio"],
            "speech_act": report_data["speech_act"],
            "insight": report_data["insight"],
        },
    )


def insert_report(report_data, reports_day):
    reports_id = execute_insert_update_query(
        query=INSERT_REPORT,
        params={
            "plans_id": report_data["plans_id"],
            "title": report_data["title"],
            "wordcloud": report_data["wordcloud"],
            "sentence_length": report_data["sentence_length"],
            "pos_ratio": report_data["pos_ratio"],
            "speech_act": report_data["speech_act"],
            "insight": report_data["insight"],
        },
        return_id=True,
    )
    return str(reports_id)


def update_reports_id_missions(reports_id, missions_ids, update_before_missions_id):
    missions_ids = [str(mission["id"]) for mission in missions_ids]
    if len(update_before_missions_id) > len(missions_ids):
        for missions_id in update_before_missions_id:
            if missions_id not in missions_ids:
                execute_insert_update_query(
                    query=DELETE_REPORTS_ID_MISSIONS,
                    params={
                        "reports_id": reports_id,
                        "missions_id": missions_id,
                    },
                )
    else:
        for missions_id in missions_ids:
            execute_insert_update_query(
                query=UPDATE_REPORTS_ID_MISSIONS,
                params={
                    "reports_id": reports_id,
                    "missions_id": missions_id,
                },
            )


def insert_reports_id_missions(reports_id, missions_ids):
    for missions_id in missions_ids:
        execute_insert_update_query(
            query=UPDATE_REPORTS_ID_MISSIONS,
            params={
                "reports_id": reports_id,
                "missions_id": missions_id["id"],
            },
        )


def slect_missions_title(reports):
    reports_with_missions = []
    for report in reports:
        report_id = report["id"]
        missions_data = execute_select_query(
            query=SELECT_MISSIONS_TITLE, params={"reports_id": report_id}
        )
        reports_with_missions.append({"report": report, "missions": missions_data})
        if missions_data is None:
            reports_with_missions.append({"report": report, "missions": []})
    return reports_with_missions


def slect_missions_id(report_id):
    missions_data = execute_select_query(
        query=SELECT_MISSIONS_TITLE, params={"reports_id": report_id}
    )
    return missions_data


def update_description_image(plans_id, description_image_name, image):
    plan = execute_select_query(
        query=SELECT_PLAN,
        params={"plans_id": plans_id},
    )
    extension = image.filename.split(".")[-1]
    image_id = generate_unique_filename(extension)
    file_content = image.file.read()
    if plan and plan[0].get("description_image_id"):
        supabase.storage.from_("plan-images").remove(plan[0]["description_image_id"])
        supabase.storage.from_("plan-images").upload(
            image_id,
            file_content,
            file_options={"content-type": image.content_type},
        )
    else:
        supabase.storage.from_("plan-images").upload(
            image_id,
            file_content,
            file_options={"content-type": image.content_type},
        )
    execute_insert_update_query(
        query=UPDATE_PLAN_DESCRIPTION_IMAGE,
        params={
            "plans_id": plans_id,
            "description_image_name": description_image_name,
            "description_image_id": image_id,
        },
    )
    return {"message": "success"}


def update_schedule_image(plans_id, schedule_image_name, image):
    plan = execute_select_query(
        query=SELECT_PLAN,
        params={"plans_id": plans_id},
    )
    extension = image.filename.split(".")[-1]
    image_id = generate_unique_filename(extension)
    file_content = image.file.read()
    if plan and plan[0].get("schedule_image_id"):
        supabase.storage.from_("plan-images").remove(plan[0]["schedule_image_id"])
        supabase.storage.from_("plan-images").upload(
            image_id,
            file_content,
            file_options={"content-type": image.content_type},
        )
    else:
        supabase.storage.from_("plan-images").upload(
            image_id,
            file_content,
            file_options={"content-type": image.content_type},
        )
    execute_insert_update_query(
        query=UPDATE_PLAN_SCHEDULE_IMAGE,
        params={
            "plans_id": plans_id,
            "schedule_image_name": schedule_image_name,
            "schedule_image_id": image_id,
        },
    )
    return {"message": "success"}


def update_thumbnail_image(plans_id, thumbnail_image_name, image):
    plan = execute_select_query(
        query=SELECT_PLAN,
        params={"plans_id": plans_id},
    )
    extension = image.filename.split(".")[-1]
    image_id = generate_unique_filename(extension)
    file_content = image.file.read()
    if plan and plan[0].get("thumbnail_image_id"):
        supabase.storage.from_("plan-images").remove(plan[0]["thumbnail_image_id"])
        supabase.storage.from_("plan-images").upload(
            image_id,
            file_content,
            file_options={"content-type": image.content_type},
        )
    else:
        supabase.storage.from_("plan-images").upload(
            image_id,
            file_content,
            file_options={"content-type": image.content_type},
        )
    execute_insert_update_query(
        query=UPDATE_PLAN_THUMBNAIL_IMAGE,
        params={
            "plans_id": plans_id,
            "thumbnail_image_name": thumbnail_image_name,
            "thumbnail_image_id": image_id,
        },
    )
    return {"message": "success"}


def generate_unique_filename(extension: str) -> str:
    return f"{uuid.uuid4().hex}.{extension}"
