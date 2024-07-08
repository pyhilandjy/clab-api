from app.db.connection import postgresql_connection
from app.db.query import (DELETE_ROW, INSERT_COPIED_DATA, SELECT_SPEECH_ACTS,
                          SELECT_STT_DATA, SELECT_TALK_MORE,
                          UPDATE_DECREASE_TEXT_ORDER,
                          UPDATE_INCREASE_TEXT_ORDER, UPDATE_REPLACE_SPEAKER,
                          UPDATE_REPLACE_TEXT_EDITED, UPDATE_SPEECH_ACT,
                          UPDATE_TALK_MORE, UPDATE_TEXT_EDITED)
from app.db.worker import execute_insert_update_query, execute_select_query


def select_stt_data_by_file_id(file_id):
    return execute_select_query(
        query=SELECT_STT_DATA,
        params={
            "file_id": file_id,
        },
    )


def update_text_edit(id, file_id, new_text, new_speaker):
    return execute_insert_update_query(
        query=UPDATE_TEXT_EDITED,
        params={
            "id": id,
            "file_id": file_id,
            "new_text": new_text,
            "new_speaker": new_speaker,
        },
    )


def update_replace_text_edit(file_id, old_text, new_text):
    execute_insert_update_query(
        query=UPDATE_REPLACE_TEXT_EDITED,
        params={
            "file_id": file_id,
            "old_text": old_text,
            "new_text": new_text,
        },
    )


def update_replace_speaker(file_id, old_speaker, new_speaker):
    execute_insert_update_query(
        query=UPDATE_REPLACE_SPEAKER,
        params={
            "file_id": file_id,
            "old_speaker": old_speaker,
            "new_speaker": new_speaker,
        },
    )


def add_row_stt_data(file_id, selected_text_order):
    with postgresql_connection.get_db() as db:
        try:
            params = {
                "file_id": file_id,
                "selected_text_order": selected_text_order,
            }
            result = db.execute(UPDATE_INCREASE_TEXT_ORDER, params)
            print(f"Affected rows: {result.rowcount}")
            result = db.execute(INSERT_COPIED_DATA, params)
            print(f"Affected rows: {result.rowcount}")
        except Exception as e:
            db.rollback()
            print(e)
            return 0
        else:
            db.commit()


def delete_row_stt_data(file_id, selected_text_order):
    with postgresql_connection.get_db() as db:
        try:
            params = {
                "file_id": file_id,
                "selected_text_order": selected_text_order,
            }
            result = db.execute(DELETE_ROW, params)
            print(f"Affected rows: {result.rowcount}")
            result = db.execute(UPDATE_DECREASE_TEXT_ORDER, params)
            print(f"Affected rows: {result.rowcount}")
        except Exception as e:
            db.rollback()
            print(e)
            return 0
        else:
            db.commit()


def select_speech_act():
    return execute_select_query(query=SELECT_SPEECH_ACTS)


def select_talk_more():
    return execute_select_query(query=SELECT_TALK_MORE)


def update_speech_act(id, act_id):
    return execute_insert_update_query(
        query=UPDATE_SPEECH_ACT,
        params={
            "id": id,
            "act_id": act_id,
        },
    )


def update_talk_more(id, talk_more_id):
    return execute_insert_update_query(
        query=UPDATE_TALK_MORE,
        params={
            "id": id,
            "talk_more_id": talk_more_id,
        },
    )
