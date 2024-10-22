from app.db.worker import execute_insert_update_query, execute_select_query

from app.db.query import SELECT_USER_REPORTS


def select_user_reports():
    return execute_select_query(query=SELECT_USER_REPORTS)
