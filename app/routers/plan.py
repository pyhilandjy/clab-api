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
)

from app.services.users import get_current_user

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
    mission = select_mission(plan_id)
    if not mission:
        return []
    return mission


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
        return JSONResponse(status_code=1001, content=response)
    elif response["Code"] == "1002":
        return JSONResponse(status_code=1002, content=response)
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
    day: Optional[int] = None
    start_age_month: Optional[int] = None
    end_age_month: Optional[int] = None
    description: Optional[str] = None
    type: Optional[str] = None
    tags: Optional[list] = None
    category_id: Optional[str] = None


@router.put("/plans/{plan_id}", tags=["Plan"])
def insert_plan(plan_id: str, payload: UpdatePlanPayload):
    try:
        update_plans(payload.model_dump())
        return {"message": "Plan successfully updated"}
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


@router.get("/category/sub/{parents_id}", tags=["Plan"])
def get_sub_category(parents_id):
    categorys = select_sub_category(parents_id)
    if not categorys:
        raise HTTPException(status_code=404, detail="Files not found")
    return categorys


@router.get("/categorys/main/", tags=["Plan"])
def get_main_category():
    categorys = select_main_category()
    if not categorys:
        raise HTTPException(status_code=404, detail="Files not found")
    return categorys


@router.get("/categories/", tags=["Plan"])
def read_categories():
    categories = get_all_categories()
    return categories


class UpdatemissionStatus(BaseModel):
    id: str
    status: str


@router.patch("/missions/status/", tags=["mission"])
def insert_mission(payload: UpdatemissionStatus):
    try:
        update_mission_status(payload.model_dump())
        return {"message": "mission successfully inserted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/missions/{mission_id}", tags=["Mission"])
async def gdel_plans(mission_id: str):
    """
    mission 삭제시 mission_message 내용도 삭제
    """
    delete_mission(mission_id)


# @router.post("/user/plans/{plan_id}", tags=["Plan"])
# # async def post_user_plan(plan_id: str, user_id: str):
# async def post_user_plan(plan_id: str, current_user=Depends(get_current_user)):
#     try:
#         user_id = current_user.get("sub")
#         if not user_id:
#             raise HTTPException(status_code=400, detail="Invalid user ID")
#         update_user_plan(user_id, plan_id)
#         return {"message": "User plan updated successfully"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get("/user/plan/", tags=["Plan"])
# async def post_user_plan(current_user=Depends(get_current_user)):
#     # async def get_user_plan(user_id):
#     try:
#         user_id = current_user.get("sub")
#         if not user_id:
#             raise HTTPException(status_code=400, detail="Invalid user ID")
#         user_plan = select_plans_user(user_id)
#         return user_plan
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
