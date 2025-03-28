from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.stt import (
    add_row_stt_data,
    delete_row_stt_data,
    response_openai_data,
    select_act_types,
    select_speech_act,
    select_stt_data_by_audio_files_id,
    select_talk_more,
    update_is_turn,
    update_replace_speaker,
    update_replace_text_edit,
    update_speech_act,
    update_stt_data_act_type,
    update_talk_more,
    update_text_edit,
)

router = APIRouter()


@router.get("/data/{audio_files_id}", tags=["STT"], response_model=list[dict])
async def get_data(audio_files_id: str):
    """audio_files_id별로 stt result를 가져오는 엔드포인트"""
    results = select_stt_data_by_audio_files_id(audio_files_id)
    if not results:
        raise HTTPException(status_code=404, detail="STT result not found")
    return results


class EditTextModel(BaseModel):
    id: str
    audio_files_id: str
    new_text: str
    new_speaker: str


# speaker 추가
@router.patch("/data/edit-text", tags=["STT"])
async def edit_text(text_edit_model: EditTextModel):
    update_text_edit(**text_edit_model.model_dump())
    return {
        "message": "STT data updated successfully",
    }


@router.patch("/data/batch-edit", tags=["STT"])
async def batch_edit(text_edit_models: List[EditTextModel]):
    for text_edit_model in text_edit_models:
        try:
            update_text_edit(**text_edit_model.model_dump())
        except HTTPException as e:
            raise HTTPException(
                status_code=404, detail=f"Row with id {text_edit_model.id} not found"
            )
    return {
        "message": "All STT data updated successfully",
    }


class ReplaceTextModel(BaseModel):
    audio_files_id: str
    old_text: str
    new_text: str


@router.patch("/data/replace-text", tags=["STT"])
async def replace_text(replace_text_model: ReplaceTextModel):
    update_replace_text_edit(**replace_text_model.model_dump())
    return {"message": "STT data replaced successfully"}


class ReplaceSpeakerModel(BaseModel):
    audio_files_id: str
    old_speaker: str
    new_speaker: str


@router.patch("/data/replace-speaker", tags=["STT"])
async def update_stt_speaker(replace_speaker_model: ReplaceSpeakerModel):
    update_replace_speaker(**replace_speaker_model.model_dump())
    return {
        "message": "STT data speaker replaced successfully",
    }


class AddSTTDataRowModel(BaseModel):
    audio_files_id: str
    selected_text_order: int


@router.post("/data/add-row", tags=["STT"])
async def add_row(add_stt_data_row_model: AddSTTDataRowModel):
    add_row_stt_data(**add_stt_data_row_model.model_dump())
    return {
        "message": "Add row updated successfully",
    }


class DeleteSTTDataRowModel(BaseModel):
    audio_files_id: str
    selected_text_order: int


@router.post("/data/delete-row", tags=["STT"])
async def delete_row(delete_stt_data_row_model: DeleteSTTDataRowModel):
    delete_row_stt_data(**delete_stt_data_row_model.model_dump())
    return {
        "message": "Delete row updated successfully",
    }


@router.get("/speech_acts", tags=["STT"], response_model=List[dict])
async def get_speech_acts():
    """speech act의 목록을 가져오는 엔드포인트"""
    acts = select_speech_act()
    if not acts:
        raise HTTPException(status_code=404, detail="speech_act not found")
    return acts


class EditSpeechActsModel(BaseModel):
    id: str
    act_id: int


@router.patch("/data/edit-speech-act", tags=["STT"])
async def edit_speech_act(act_id_update: EditSpeechActsModel):
    update_speech_act(**act_id_update.model_dump())
    return {
        "message": "STT data updated successfully",
    }


@router.get("/talk_more", tags=["STT"], response_model=List[dict])
async def get_talk_more():
    """speech act의 목록을 가져오는 엔드포인트"""
    act = select_talk_more()
    if not act:
        raise HTTPException(status_code=404, detail="talk_more not found")
    return act


class EditSpeechTalkMoresModel(BaseModel):
    id: str
    talk_more_id: int


@router.patch("/data/edit-talk-more", tags=["STT"])
async def edit_talk_more_id(talk_more_id_update: EditSpeechTalkMoresModel):
    update_talk_more(**talk_more_id_update.model_dump())
    return {
        "message": "STT data updated successfully",
    }


@router.get(
    "/act_types",
    tags=["STT"],
)
async def get_act_types():
    """act type의 목록을 가져오는 엔드포인트"""
    act_types = select_act_types()
    if not act_types:
        raise HTTPException(status_code=404, detail="act_types not found")
    return act_types


@router.patch("/speech-act/{audio_files_id}", tags=["LLM"])
async def patch_speech_act_type(audio_files_id: str):
    """llm 을 사용하여 화행 수정 앤드포인트"""
    response = response_openai_data(audio_files_id)
    update_stt_data_act_type(response)
    return "success"


class EditSpeechActTypeModel(BaseModel):
    act_types_id: int
    id: str


@router.patch("/data/edit-act-type", tags=["STT"])
def edit_act_type(edit_speech_act_type_model: EditSpeechActTypeModel):
    update_stt_data_act_type(**edit_speech_act_type_model.model_dump())
    return {
        "message": "STT data updated successfully",
    }


class EditTurnModel(BaseModel):
    id: str
    is_turn: bool


@router.patch("/data/is-turn", tags=["STT"])
def edit_turn(edit_turn_model: EditTurnModel):
    update_is_turn(**edit_turn_model.model_dump())
    return {
        "message": "STT data updated successfully",
    }


@router.get("/data/{audio_files_id}/report/quaritative", tags=["STT"])
def report_detail(audio_files_id: str):
    """
    질적분석 불러오는 앤드포인트
    """
    result = response_openai_data(audio_files_id)
    return result


class OpenaiDataModel(BaseModel):
    alternative: str
    description: str
    expectation: str
    mood: str
    stt_data_id: str


# @router.post("/data/report/quaritative", tags=["STT"])
# def report_detail(openai_data_model: OpenaiDataModel):
#     """
#     질적분석 저장하는 앤드포인트
#     """
#     post_openai_data(openai_data_model.model_dump())
