from app.db.query import SELECT_PLANS, SELECT_MISSION
from app.db.worker import execute_insert_update_query, execute_select_query


def select_plans():
    return execute_select_query(query=SELECT_PLANS)


def select_mission(plan_id):
    return execute_select_query(
        query=SELECT_MISSION,
        params={
            "plan_id": plan_id,
        },
    )
