from fastapi import APIRouter, HTTPException
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
)

router = APIRouter()


@router.get("/plans/", tags=["Plan"])
async def get_plans():
    """
    plan 데이터를 가져오는 엔드포인트
    """
    file_ids = select_plans()
    if not file_ids:
        raise HTTPException(status_code=404, detail="Files not found")
    return file_ids


@router.get("/missions/{plan_id}", tags=["Mission"])
async def get_missions(plan_id: str):
    """
    plan_id 별 mission 데이터를 가져오는 엔드포인트
    """
    file_ids = select_mission(plan_id)
    if not file_ids:
        raise HTTPException(status_code=404, detail="Files not found")
    return file_ids


@router.get("/plans/{plan_id}", tags=["Plans"])
async def get_plans(plan_id: str):
    """
    plan_id 별 plan 데이터를 가져오는 엔드포인트
    """
    file_ids = select_plan(plan_id)
    if not file_ids:
        raise HTTPException(status_code=404, detail="Files not found")
    return file_ids


@router.delete("/plans/{plan_id}", tags=["Plan"])
async def gdel_plans(plan_id: str):
    """
    plan_id 별 plan을 삭제 (mission이 존재할 경우 삭제 불가능)
    """
    response_json = delete_plan(plan_id)
    response = json.loads(response_json)

    if response["Code"] == "1001":
        return JSONResponse(status_code=400, content=response)
    elif response["Code"] == "1002":
        return JSONResponse(status_code=500, content=response)
    elif response["Code"] == "0":
        return response
    else:
        return JSONResponse(
            status_code=500, content={"code": "9999", "message": "Unknown error"}
        )


class PlanPayload(BaseModel):
    plan_name: str
    price: Optional[int] = None
    start_age_month: Optional[int] = None
    end_age_month: Optional[int] = None
    description: Optional[str] = None


@router.post("/plans/", tags=["Plan"])
def insert_plan(payload: PlanPayload):
    try:
        insert_plans(payload.model_dump())
        return {"message": "Plan successfully inserted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/plans/{plan_id}", tags=["Plan"])
async def get_plans(plan_id):
    """
    plan 데이터를 가져오는 엔드포인트
    """
    file_ids = select_plan(plan_id)
    if not file_ids:
        raise HTTPException(status_code=404, detail="Files not found")
    return file_ids


class UpdatePlanPayload(BaseModel):
    id: str
    plan_name: str
    price: Optional[int] = None
    start_age_month: Optional[int] = None
    end_age_month: Optional[int] = None
    description: Optional[str] = None


@router.put("/plans/", tags=["Plan"])
def insert_plan(payload: UpdatePlanPayload):
    try:
        update_plans(payload.model_dump())
        return {"message": "Plan successfully inserted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class UpdatePlanStatus(BaseModel):
    id: str
    status: str


@router.patch("/plan/status/", tags=["Plan"])
def insert_plan(payload: UpdatePlanStatus):
    try:
        update_plan_status(payload.model_dump())
        return {"message": "Plan successfully inserted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
