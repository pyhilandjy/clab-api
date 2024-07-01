import requests
from typing import Dict
import uuid
import jwt

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse

import supabase
from supabase import create_client, Client

from app.config import settings

router = APIRouter()

supabase: Client = create_client(settings.supabase_url, settings.supabase_service_key)


@router.get("/all_users")
def get_all_users():
    try:
        # Supabase Auth API를 사용하여 유저 정보 가져오기
        response = supabase.auth.admin.list_users()
        users = response
        return users
    except Exception as e:
        return {"error": str(e)}


def get_user_id_from_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.supabase_jwt_key, algorithms=["HS256"])
        return payload.get("id")
    except jwt.PyJWTError:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
