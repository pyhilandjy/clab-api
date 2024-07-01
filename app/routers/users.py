import requests
from typing import Dict
import uuid
import jwt

from fastapi import APIRouter, HTTPException

import supabase
from supabase import create_client, Client

from app.config import settings

router = APIRouter()

supabase: Client = create_client(settings.supabase_url, settings.supabase_service_key)


@router.get("/users/", tags=["users"])
def get_all_users():
    try:
        response = supabase.auth.admin.list_users()
        users = response
        user_list = []
        for user in users:
            user_info = {
                "id": user.id,
                "name": user.user_metadata.get("name", ""),
                "email": user.email,
            }
            user_list.append(user_info)

        return user_list
    except Exception as e:
        return {"error": str(e)}


def get_user_id_from_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.supabase_jwt_key, algorithms=["HS256"])
        return payload.get("id")
    except jwt.PyJWTError:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
