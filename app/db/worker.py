from app.db.connection import postgresql_connection


def execute_select_query(query: str, params: dict = None) -> list:
    """
    SELECT 쿼리를 실행합니다.
    :param connection: DB 연결 객체.
    :type connection: DBConnection

    :param query: 실행할 쿼리.
    :type query: str

    :param params: 쿼리 파라미터.
    :type params: dict

    :return: 쿼리 결과.
    :rtype: list
    """
    with postgresql_connection.get_db() as db:
        result = db.execute(query, params)
        return [record for record in result.mappings()]


def execute_insert_update_query(
    query: str, params: dict = None, return_id: bool = False
) -> None:
    """
    INSERT 또는 UPDATE 쿼리를 실행합니다.
    :param connection: DB 연결 객체.
    :type connection: DBConnection

    :param query: 실행할 쿼리.
    :type query: str

    :param params: 쿼리 파라미터.
    :type params: dict
    """
    with postgresql_connection.get_db() as db:
        try:
            result = db.execute(query, params)
            print(f"Affected rows: {result.rowcount}")
            inserted_id = None
            if return_id:
                inserted_id = result.fetchone()[0]
        except Exception as e:
            db.rollback()
            print(e)
            return 0
        else:
            db.commit()
            if inserted_id:
                return inserted_id
