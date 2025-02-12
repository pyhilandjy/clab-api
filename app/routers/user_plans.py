from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.user_plans import select_user_plans, delete_user_package

router = APIRouter()


@router.get("/user_plans", tags=["User_Plan"])
def get_user_plans():
    return select_user_plans()


@router.delete("/user_plans/{user_plans_id}", tags=["User_Plan"])
def delete_user_packages(user_plans_id: str):
    return delete_user_package(user_plans_id)
