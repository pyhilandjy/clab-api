import json
from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.services.plan import (
    delete_mission,
    delete_plan,
    delete_report,
    get_all_categories,
    insert_mission,
    insert_plans,
    insert_report,
    insert_reports_id_missions,
    select_main_category,
    select_mission,
    select_plan,
    select_plans,
    select_reports,
    select_sub_category,
    slect_missions_id,
    slect_missions_title,
    update_mission,
    update_mission_status,
    update_plan_status,
    update_plans,
    update_report,
    update_reports_id_missions,
    update_description_image,
    update_schedule_image,
    update_thumbnail_image,
    delete_plan_image,
)

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
    # 삭제시 이미지가 존재할 경우 스토리지에서 삭제 요구
    delete_plan_image(plans_id)
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
    summary: Optional[str] = None
    schedule: Optional[str] = None


@router.post("/plans", tags=["Plans"])
def insert_plan(
    plan_name: str = Form(...),
    price: Optional[int] = Form(None),
    day: Optional[int] = Form(None),
    start_age_month: Optional[int] = Form(None),
    end_age_month: Optional[int] = Form(None),
    description: Optional[str] = Form(None),
    type: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    category_id: Optional[str] = Form(None),
    summary: Optional[str] = Form(None),
    schedule: Optional[str] = Form(None),
    description_image: Optional[UploadFile] = File(...),
    description_image_name: Optional[str] = Form(...),
    thumbnail_image: Optional[UploadFile] = File(...),
    thumbnail_image_name: Optional[str] = Form(...),
    schedule_image: Optional[UploadFile] = File(...),
    schedule_image_name: Optional[str] = Form(...),
):
    payload = {
        "plan_name": plan_name,
        "price": price,
        "day": day,
        "start_age_month": start_age_month,
        "end_age_month": end_age_month,
        "description": description,
        "type": type,
        "tags": eval(tags),
        "category_id": category_id,
        "summary": summary,
        "schedule": schedule,
    }
    try:
        # 플랜 데이터 삽입
        plans_id = insert_plans(payload)
        plans_id = str(plans_id)
        # 이미지 업로드
        if description_image:
            update_description_image(
                plans_id, description_image_name, description_image
            )
        if thumbnail_image:
            update_thumbnail_image(plans_id, thumbnail_image_name, thumbnail_image)
        if schedule_image:
            update_schedule_image(plans_id, schedule_image_name, schedule_image)

        return {"message": "Plan and images successfully created"}
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
    summary: Optional[str] = None
    schedule: Optional[str] = None


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
    summary: str
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
    summary: str
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
    reports_missions = slect_missions_title(reports)
    return reports_missions


@router.delete("/reports/{report_id}", tags=["Reports"])
async def delete_reports(report_id: str):
    """
    report 삭제
    """
    delete_report(report_id)


class ReportUpdate(BaseModel):
    title: str
    wordcloud: Optional[bool] = False
    sentence_length: Optional[bool] = False
    pos_ratio: Optional[bool] = False
    speech_act: Optional[bool] = False
    insight: Optional[bool] = False
    missions_id: list[dict]


# todo 연결된 missions_id에서 삭제된 것들은 null로 처리해야함
# 기존 데이터를 조회해서 missions_id를 가져와서 비교해서 삭제된 것들은 null로 처리해야함
# 불러와야 하는 데이터는 missions_id 이고 missions테이블에 reports_id가 있는 것을 가져와서 비교해야함
# if len(missions_id) > len(update_before_missions_id) => insert
# else => update null로 처리
@router.put("/reports/{report_id}", tags=["Reports"])
async def put_reports(report_id: str, payload: ReportUpdate):
    """
    report 업데이트
    """
    update_before_missions = slect_missions_id(report_id)
    update_before_missions_id = [
        str(mission["id"]) for mission in update_before_missions
    ]
    report_data = payload.model_dump()
    report_data["id"] = report_id
    missions_ids = payload.missions_id
    update_report(report_data)
    update_reports_id_missions(report_id, missions_ids, update_before_missions_id)
    return {"message": "success"}


class ReportCreate(BaseModel):
    title: str
    wordcloud: bool
    sentence_length: bool
    pos_ratio: bool
    speech_act: bool
    insight: bool
    missions_id: list[dict]


# todo 리스트의 값들은 전부 다르게 처리해야함 각 컬럼이 생성이 되어야하고, analysis는 bools로 missions_id는 바뀌어서 missions 테이블에 reports_id 가 들어가야함


@router.post("/reports/{plans_id}", tags=["Reports"])
async def post_reports(plans_id: str, payload: ReportCreate):
    """
    report 추가
    """
    report_data = payload.model_dump()
    report_data["plans_id"] = plans_id
    reports_day = len(report_data["missions_id"])
    reports_id = insert_report(report_data, reports_day)
    missions_ids = payload.missions_id
    insert_reports_id_missions(reports_id, missions_ids)
    return {"message": "success"}


@router.patch("/plans/{plans_id}/description/image", tags=["Plans"])
async def patch_description_image(
    plans_id: str,
    description_image_name: str = Form(...),
    image: UploadFile = File(...),
):
    """
    plan description image 업데이트
    """
    return update_description_image(plans_id, description_image_name, image)


@router.patch("/plans/{plans_id}/schedule/image", tags=["Plans"])
async def patch_schedule_image(
    plans_id: str,
    schedule_image_name: str = Form(...),
    image: UploadFile = File(...),
):
    """
    plan schedule image 업데이트
    """
    return update_schedule_image(plans_id, schedule_image_name, image)


@router.patch("/plans/{plans_id}/thumbnail/image", tags=["Plans"])
async def patch_thumbnail_image(
    plans_id: str,
    thumbnail_image_name: str = Form(...),
    image: UploadFile = File(...),
):
    """
    Plan의 썸네일 이미지 업데이트
    """
    return update_thumbnail_image(plans_id, thumbnail_image_name, image)
