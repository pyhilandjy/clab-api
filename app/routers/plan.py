from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
from typing import Optional

from app.services.plan import (
    select_plans,
    select_mission,
    delete_plan,
    insert_plans,
    update_plans,
    select_plan,
    update_plan_status,
    update_mission_status,
    delete_mission,
    select_sub_category,
    select_main_category,
    get_all_categories,
    insert_mission,
    update_mission,
    select_reports,
)

from app.services.users import get_current_user
import requests

router = APIRouter()


@router.get("/plans/", tags=["Plans"])
async def get_plans():
    """
    plan 데이터를 가져오는 엔드포인트
    """
    plans = select_plans()
    if not plans:
        raise HTTPException(status_code=404, detail="Files not found")
    return plans


@router.get("/missions/{plans_id}", tags=["Missions"])
async def get_missions(plans_id: str):
    """
    plans_id 별 mission 데이터를 가져오는 엔드포인트
    """
    mission = select_mission(plans_id)
    if not mission:
        return []
    return mission


@router.get("/plans/{plans_id}", tags=["Plans"])
async def get_plans(plans_id: str):
    """
    plans_id 별 plan 데이터를 가져오는 엔드포인트
    """
    plan = select_plan(plans_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Files not found")
    return plan


@router.delete("/plans/{plans_id}", tags=["Plans"])
async def gdel_plans(plans_id: str):
    """
    plans_id 별 plan을 삭제 (mission이 존재할 경우 삭제 불가능)
    """
    response_json = delete_plan(plans_id)
    response = json.loads(response_json)

    if response["Code"] == "1001":
        return JSONResponse(status_code=200, content=response)
    elif response["Code"] == "1002":
        return JSONResponse(status_code=400, content=response)
    elif response["Code"] == "0":
        return response
    else:
        return JSONResponse(
            status_code=500, content={"code": "9999", "message": "Unknown error"}
        )


class PlanPayload(BaseModel):
    plan_name: str
    price: Optional[int] = None
    day: Optional[int] = None
    start_age_month: Optional[int] = None
    end_age_month: Optional[int] = None
    description: Optional[str] = None
    type: Optional[str] = None
    tags: Optional[list] = None
    category_id: Optional[str] = None


@router.post("/plans/", tags=["Plans"])
def insert_plan(payload: PlanPayload):
    try:
        insert_plans(payload.model_dump())
        return {"message": "Plan successfully inserted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class UpdatePlanPayload(BaseModel):
    id: str
    plan_name: str
    price: Optional[int] = None
    day: Optional[int] = None
    start_age_month: Optional[int] = None
    end_age_month: Optional[int] = None
    description: Optional[str] = None
    type: Optional[str] = None
    tags: Optional[list] = None
    category_id: Optional[str] = None


@router.put("/plans/{plans_id}", tags=["Plans"])
def insert_plan(plans_id: str, payload: UpdatePlanPayload):
    try:
        update_plans(payload.model_dump())
        return {"message": "Plan successfully updated"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class UpdatePlanStatus(BaseModel):
    status: str


@router.patch("/plans/{plan_id}/status/", tags=["Plans"])
def insert_plan(plan_id: str, payload: UpdatePlanStatus):
    try:
        update_plan_status(plan_id, payload.status)
        return {"message": "Plan successfully inserted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/categories/sub/{parents_id}", tags=["Plans"])
def get_sub_category(parents_id):
    categories = select_sub_category(parents_id)
    if not categories:
        raise HTTPException(status_code=404, detail="Files not found")
    return categories


@router.get("/categories/main/", tags=["Plans"])
def get_main_category():
    categories = select_main_category()
    if not categories:
        raise HTTPException(status_code=404, detail="Files not found")
    return categories


@router.get("/categories/", tags=["Plans"])
def read_categories():
    categories = get_all_categories()
    return categories


class UpdatemissionStatus(BaseModel):
    id: str
    status: str


@router.patch("/missions/status/", tags=["Missions"])
def petch_mission_status(payload: UpdatemissionStatus):
    try:
        update_mission_status(payload.model_dump())
        return {"message": "mission successfully inserted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/missions/{mission_id}", tags=["Missions"])
async def gdel_plans(mission_id: str):
    """
    mission 삭제시 mission_message 내용도 삭제
    """
    delete_mission(mission_id)


class InsertMission(BaseModel):
    title: str
    summation: str
    day: int
    message: str


@router.post("/missions/{plans_id}", tags=["Missions"])
async def post_missions(plans_id: str, payload: InsertMission):
    """
    plans_id 별 mission 데이터를 추가하는 엔드포인트
    """
    mission_data = payload.model_dump()
    mission_data["plans_id"] = plans_id
    insert_mission(mission_data)
    return {"message": "success"}


class UpdateMission(BaseModel):
    title: str
    summation: str
    day: int
    message: str


@router.patch("/missions/{mission_id}", tags=["Missions"])
async def patch_missions(mission_id: str, payload: UpdateMission):
    """
    plans_id 별 mission 데이터를 추가하는 엔드포인트
    """
    mission_data = payload.model_dump()
    mission_data["id"] = mission_id
    update_mission(mission_data)
    return {"message": "success"}


@router.get("/reports/{plans_id}", tags=["Reports"])
async def get_reports(plans_id: str):
    """
    plans_id 별 mission 데이터를 가져오는 엔드포인트
    """
    reports = select_reports(plans_id)
    if not reports:
        return []
    return reports
