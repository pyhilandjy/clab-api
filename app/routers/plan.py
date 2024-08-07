from fastapi import APIRouter, HTTPException

from app.services.plan import select_plans, select_mission

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
