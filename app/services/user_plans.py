from app.db.worker import execute_insert_update_query, execute_select_query
from app.db.user_plan_query import SELECT_USER_PLANS, DELETE_USER_PACKAGE
from app.services.users import fetch_user_info


def select_user_plans():
    datas = execute_select_query(query=SELECT_USER_PLANS, params={})
    datas = [dict(data) for data in datas]
    for data in datas:
        data["user_id"] = str(data["user_id"])
        user_info = fetch_user_info(data["user_id"])
        data["user_name"] = user_info["user_name"]
        data["user_created_at"] = user_info["user_created_at"]
    return datas


def delete_user_package(user_plans_id):
    execute_insert_update_query(
        query=DELETE_USER_PACKAGE,
        params={"user_plans_id": user_plans_id},
    )
    return {"message": "success"}
