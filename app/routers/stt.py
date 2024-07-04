from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.stt import (
    add_row_stt_data,
    delete_row_stt_data,
    select_speech_act,
    select_stt_data_by_file_id,
    update_replace_speaker,
    update_replace_text_edit,
    update_speech_act,
    update_text_edit,
    update_talk_more,
    select_talk_more,
)

router = APIRouter()


@router.get("/data/{file_id}", tags=["STT"], response_model=list[dict])
async def get_data(file_id: str):
    """file_id별로 stt result를 가져오는 엔드포인트"""
    results = select_stt_data_by_file_id(file_id)
    if not results:
        raise HTTPException(status_code=404, detail="STT result not found")
    return results


class EditTextModel(BaseModel):
    id: str
    file_id: str
    new_text: str
    new_speaker: str


# speaker 추가
@router.patch("/data/edit-text/", tags=["STT"])
async def edit_text(text_edit_model: EditTextModel):
    update_text_edit(**text_edit_model.model_dump())
    return {
        "message": "STT data updated successfully",
    }


class ReplaceTextModel(BaseModel):
    file_id: str
    old_text: str
    new_text: str


@router.patch("/data/replace-text/", tags=["STT"])
async def replace_text(replace_text_model: ReplaceTextModel):
    update_replace_text_edit(**replace_text_model.model_dump())
    return {"message": "STT data replaced successfully"}


class ReplaceSpeakerModel(BaseModel):
    file_id: str
    old_speaker: str
    new_speaker: str


@router.patch("/data/replace-speaker/", tags=["STT"])
async def update_stt_speaker(replace_speaker_model: ReplaceSpeakerModel):
    update_replace_speaker(**replace_speaker_model.model_dump())
    return {
        "message": "STT data speaker replaced successfully",
    }


class AddSTTDataRowModel(BaseModel):
    file_id: str
    selected_text_order: int


@router.post("/data/add-row/", tags=["STT"])
async def add_row(add_stt_data_row_model: AddSTTDataRowModel):
    add_row_stt_data(**add_stt_data_row_model.model_dump())
    return {
        "message": "Add row updated successfully",
    }


class DeleteSTTDataRowModel(BaseModel):
    file_id: str
    selected_text_order: int


@router.post("/data/delete-row/", tags=["STT"])
async def delete_row(delete_stt_data_row_model: DeleteSTTDataRowModel):
    delete_row_stt_data(**delete_stt_data_row_model.model_dump())
    return {
        "message": "Delete row updated successfully",
    }


@router.get("/speech_acts/", tags=["STT"], response_model=List[dict])
async def get_speech_acts():
    """speech act의 목록을 가져오는 엔드포인트"""
    acts = select_speech_act()
    if not acts:
        raise HTTPException(status_code=404, detail="speech_act not found")
    return acts


class EditSpeechActsModel(BaseModel):
    id: str
    act_id: int


@router.patch("/data/edit-speech-act/", tags=["STT"])
async def edit_speech_act(act_id_update: EditSpeechActsModel):
    update_speech_act(**act_id_update.model_dump())
    return {
        "message": "STT data updated successfully",
    }


@router.get("/talk_more/", tags=["STT"], response_model=List[dict])
async def get_talk_more():
    """speech act의 목록을 가져오는 엔드포인트"""
    act = select_talk_more()
    if not act:
        raise HTTPException(status_code=404, detail="talk_more not found")
    return act


class EditSpeechTalkMoresModel(BaseModel):
    id: str
    talk_more_id: int


@router.patch("/data/edit-talk-more/", tags=["STT"])
async def edit_talk_more_id(talk_more_id_update: EditSpeechTalkMoresModel):
    update_talk_more(**talk_more_id_update.model_dump())
    return {
        "message": "STT data updated successfully",
    }
