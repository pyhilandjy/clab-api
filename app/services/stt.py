import datetime
import json
from typing import List
from enum import Enum
from uuid import UUID
import re

from openai import OpenAI

from app.config import settings
from app.db.connection import postgresql_connection
from app.db.query import (
    DELETE_ROW,
    INSERT_COPIED_DATA,
    SELECT_ACT_TYPES,
    SELECT_LLM_DATA,
    SELECT_PROMPT,
    SELECT_SPEECH_ACTS,
    SELECT_STT_DATA,
    SELECT_TALK_MORE,
    SELECT_TEXT_EDITED_DATA,
    UPDATE_ACT_ID,
    UPDATE_AUDIO_FILES_IS_EDIT,
    UPDATE_DECREASE_TEXT_ORDER,
    UPDATE_INCREASE_TEXT_ORDER,
    UPDATE_IS_TURN,
    UPDATE_REPLACE_SPEAKER,
    UPDATE_REPLACE_TEXT_EDITED,
    UPDATE_SPEECH_ACT,
    UPDATE_TALK_MORE,
    UPDATE_TEXT_EDITED,
)
from app.db.worker import execute_insert_update_query, execute_select_query


def select_stt_data_by_audio_files_id(audio_files_id):
    return execute_select_query(
        query=SELECT_STT_DATA,
        params={
            "audio_files_id": audio_files_id,
        },
    )


def select_text_edited_data(audio_files_id):
    # 쿼리 실행
    results = execute_select_query(
        query=SELECT_TEXT_EDITED_DATA,
        params={"audio_files_id": audio_files_id},
    )

    modified_results = []
    for result in results:
        # Row 객체를 딕셔너리로 변환
        result_dict = dict(result)

        # UUID를 문자열로 변환
        if "id" in result_dict and isinstance(result_dict["id"], UUID):
            result_dict["id"] = str(result_dict["id"])

        modified_results.append(result_dict)

    return modified_results


def update_text_edit(id, audio_files_id, new_text, new_speaker):
    execute_insert_update_query(
        query=UPDATE_TEXT_EDITED,
        params={
            "id": id,
            "audio_files_id": audio_files_id,
            "new_text": new_text,
            "new_speaker": new_speaker,
        },
    )
    edited_at = datetime.datetime.now()
    execute_insert_update_query(
        query=UPDATE_AUDIO_FILES_IS_EDIT,
        params={
            "audio_files_id": audio_files_id,
            "is_edited": True,
            "edited_at": edited_at,
        },
    )


def update_replace_text_edit(audio_files_id, old_text, new_text):
    execute_insert_update_query(
        query=UPDATE_REPLACE_TEXT_EDITED,
        params={
            "audio_files_id": audio_files_id,
            "old_text": old_text,
            "new_text": new_text,
        },
    )
    edited_at = datetime.datetime.now()
    execute_insert_update_query(
        query=UPDATE_AUDIO_FILES_IS_EDIT,
        params={
            "audio_files_id": audio_files_id,
            "is_edited": True,
            "edited_at": edited_at,
        },
    )


def update_replace_speaker(audio_files_id, old_speaker, new_speaker):
    execute_insert_update_query(
        query=UPDATE_REPLACE_SPEAKER,
        params={
            "audio_files_id": audio_files_id,
            "old_speaker": old_speaker,
            "new_speaker": new_speaker,
        },
    )
    edited_at = datetime.datetime.now()
    execute_insert_update_query(
        query=UPDATE_AUDIO_FILES_IS_EDIT,
        params={
            "audio_files_id": audio_files_id,
            "is_edited": True,
            "edited_at": edited_at,
        },
    )


def add_row_stt_data(audio_files_id, selected_text_order):
    with postgresql_connection.get_db() as db:
        try:
            params = {
                "audio_files_id": audio_files_id,
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


def delete_row_stt_data(audio_files_id, selected_text_order):
    with postgresql_connection.get_db() as db:
        try:
            params = {
                "audio_files_id": audio_files_id,
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


def select_act_types():
    return execute_select_query(query=SELECT_ACT_TYPES)


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


def get_act_id(act_name: str):
    """
    act_name에 해당하는 act_id를 가져오는 함수
    """
    speech_acts = select_speech_act()
    for speech_act in speech_acts:
        if speech_act["act_name"] == act_name:
            return speech_act["id"]


def update_is_turn(id, is_turn):
    return execute_insert_update_query(
        query=UPDATE_IS_TURN,
        params={
            "id": id,
            "is_turn": is_turn,
        },
    )


# openai api
openai_client = OpenAI(
    api_key=settings.openai_api_key,
)


class OpenAIModel(Enum):
    GPT_4O = "chatgpt-4o-latest"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_35_TURBO = "gpt-3.5-turbo"


def openai_request(
    datas: List[dict],
    prompts: List[dict],
):
    # system_prompt, user_prompt를 문자열로 변환
    system_prompt = prompts[0]["system_prompt"]
    user_prompt = prompts[0]["user_prompt"]

    for item in datas:
        user_prompt += f"- ID {item['id']}: {item['text_edited']}\n"

    # -- set messages
    messages = []

    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    if user_prompt:
        messages.append({"role": "user", "content": user_prompt})

    completion = openai_client.chat.completions.create(
        model=OpenAIModel.GPT_4O.value,
        messages=messages,
        temperature=0.0,
    )
    assistant_message = completion.choices[0].message

    return assistant_message


def select_llm_data(audio_files_id):
    # 쿼리 실행
    results = execute_select_query(
        query=SELECT_LLM_DATA,
        params={"audio_files_id": audio_files_id},
    )

    modified_results = []
    for result in results:
        # Row 객체를 딕셔너리로 변환
        result_dict = dict(result)

        # UUID를 문자열로 변환
        if "id" in result_dict and isinstance(result_dict["id"], UUID):
            result_dict["id"] = str(result_dict["id"])

        modified_results.append(result_dict)

    return modified_results


# 추후 purpose에 따라 다른 prompt를 가져오도록 수정
def response_openai_data(audio_files_id):
    prompts = execute_select_query(
        query=SELECT_PROMPT, params={"purpose": "speech_acts"}
    )
    datas = select_llm_data(audio_files_id)
    response = openai_request(datas, prompts)
    try:
        content = response.content
        clean_content = (
            content.replace("```json", "")
            .replace("```", "")
            .replace("output =", "")
            .strip()
        )
    except AttributeError:
        return "No response from OpenAI"

    result = json.loads(clean_content)
    return result


def update_stt_data_act_type(response: list[dict]):
    """
    stt_data 테이블의 act_id 및 act_type_id를 업데이트하는 함수
    """
    converted = replace_act_name_with_act_id(response)

    for row in converted:
        execute_insert_update_query(
            query=UPDATE_ACT_ID, params={"id": row["id"], "act_id": row["act_id"]}
        )


def replace_act_name_with_act_id(response: list[dict]) -> list[dict]:
    """
    response에 있는 act_name을 DB에서 가져온 act_id로 변환하는 함수
    """
    act_types = select_speech_act()
    mapping = {act["act_name"].lower(): act["id"] for act in act_types}

    result = []
    for item in response:
        act_name = item.get("act_name", "").lower()
        act_id = mapping.get(act_name)
        if act_id:
            result.append({"id": item["id"], "act_id": act_id})
        else:
            raise ValueError(f"Unknown act_name: {act_name}")

    return result
