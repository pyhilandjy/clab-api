from app.db.connection import postgresql_connection
from uuid import UUID
from openai import OpenAI
from enum import Enum
import json
import requests
from fastapi import HTTPException
from app.db.query import (
    DELETE_ROW,
    INSERT_COPIED_DATA,
    SELECT_SPEECH_ACTS,
    SELECT_STT_DATA,
    SELECT_TALK_MORE,
    UPDATE_DECREASE_TEXT_ORDER,
    UPDATE_INCREASE_TEXT_ORDER,
    UPDATE_REPLACE_SPEAKER,
    UPDATE_REPLACE_TEXT_EDITED,
    UPDATE_SPEECH_ACT,
    UPDATE_TALK_MORE,
    UPDATE_TEXT_EDITED,
    SELECT_TEXT_EDITED_DATA,
    SELECT_ACT_TYPES,
    UPDATE_SPEECHACT_TYPE,
    UPDATE_ACT_TYPE,
    UPDATE_IS_TURN,
    SELECT_PROMPT,
    SELECT_LLM_DATA,
)
from app.config import settings
from app.db.worker import execute_insert_update_query, execute_select_query


def select_stt_data_by_audio_files_id(audio_files_id):
    return execute_select_query(
        query=SELECT_STT_DATA,
        params={
            "audio_files_id": audio_files_id,
        },
    )


# def select_text_edited_data(audio_files_id):
#     return execute_select_query(
#         query=SELECT_TEXT_EDITED_DATA,
#         params={
#             "audio_files_id": audio_files_id,
#         },
#     )


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
    return execute_insert_update_query(
        query=UPDATE_TEXT_EDITED,
        params={
            "id": id,
            "audio_files_id": audio_files_id,
            "new_text": new_text,
            "new_speaker": new_speaker,
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


def update_replace_speaker(audio_files_id, old_speaker, new_speaker):
    execute_insert_update_query(
        query=UPDATE_REPLACE_SPEAKER,
        params={
            "audio_files_id": audio_files_id,
            "old_speaker": old_speaker,
            "new_speaker": new_speaker,
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


def get_speech_act_ml(stt_data: list[dict]):
    """
    ML 서버에 요청을 보내는 엔드포인트
    """
    url = "http://114.110.130.27:5000/predict"
    headers = {"Content-Type": "application/json"}

    # 요청 데이터를 JSON 형식으로 전송
    response = requests.post(url, headers=headers, json=stt_data)

    # 응답 처리
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=500, detail="ML server error")


def get_act_id(act_name: str):
    """
    act_name에 해당하는 act_id를 가져오는 함수
    """
    speech_acts = select_speech_act()
    for speech_act in speech_acts:
        if speech_act["act_name"] == act_name:
            return speech_act["id"]


def update_ml_act_type(id: str, act_id: str, act_types_id: str):
    """
    stt_data 테이블의 act_id 및 act_type_id를 업데이트하는 함수
    """
    return execute_insert_update_query(
        query=UPDATE_SPEECHACT_TYPE,
        params={
            "id": id,
            "act_id": act_id,
            "act_types_id": act_types_id,
        },
    )


def update_stt_data_act_type(id, act_types_id):
    """
    stt_data 테이블의 act_id 및 act_type_id를 업데이트하는 함수
    """
    return execute_insert_update_query(
        query=UPDATE_ACT_TYPE,
        params={
            "id": id,
            "act_types_id": act_types_id,
        },
    )


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
    user_input: str,
    system_prompt: str | None = None,
    model: str = OpenAIModel.GPT_4O,
    temperature: float = 0.5,
    max_tokens: int = 1000,
):
    user_input_str = f"{str(user_input)}"
    # -- set messages
    messages = []

    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    if user_input:
        messages.append({"role": "user", "content": user_input_str})

    completion = openai_client.chat.completions.create(
        model=model.value,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return completion.choices[0].message


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


def create_openai_data(audio_files_id):
    system_prompt = execute_select_query(
        query=SELECT_PROMPT,
    )
    user_input = select_llm_data(audio_files_id)
    system_prompt = system_prompt[0]["prompt"]
    result = openai_request(user_input, system_prompt)
    content = result.content
    clean_content = content.strip("`").strip("json").strip()
    content = json.loads(clean_content)
    return content
