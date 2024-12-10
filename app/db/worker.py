from sqlalchemy import text

from app.db.connection import postgresql_connection


def set_timezone(db, timezone: str = "Asia/Seoul"):
    db.execute(text(f"SET TIME ZONE '{timezone}'"))


def execute_select_query(query: str, params: dict = None) -> list:
    """
    SELECT 쿼리를 실행합니다.
    :param query: 실행할 쿼리.
    :type query: str 또는 TextClause

    :param params: 쿼리 파라미터.
    :type params: dict

    :return: 쿼리 결과.
    :rtype: list
    """
    with postgresql_connection.get_db() as db:
        set_timezone(db)
        result = db.execute(query, params)
        return [record for record in result.mappings()]


def execute_insert_update_query(
    query: str, params: dict = None, return_id: bool = False
) -> None:
    """
    INSERT 또는 UPDATE 쿼리를 실행합니다.
    :param query: 실행할 쿼리.
    :type query: str 또는 TextClause

    :param params: 쿼리 파라미터.
    :type params: dict

    :param return_id: True이면 삽입된 ID를 반환합니다.
    :type return_id: bool
    """
    with postgresql_connection.get_db() as db:
        try:
            set_timezone(db)
            result = db.execute(query, params)
            print(f"Affected rows: {result.rowcount}")
            inserted_id = None
            if return_id:
                inserted_id = result.fetchone()[0]
        except Exception as e:
            db.rollback()
            print(f"Exception occurred: {e}")
            return 0
        else:
            db.commit()
            if return_id:
                return inserted_id
            else:
                return result.rowcount
