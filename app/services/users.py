from typing import Dict

import jwt
from fastapi import APIRouter
from supabase import Client, create_client

from app.config import settings

router = APIRouter()

supabase: Client = create_client(settings.supabase_url, settings.supabase_service_key)

JWT_AUDIENCE = "authenticated"


def get_user_info_from_token(token: str) -> str:

    payload = jwt.decode(
        token,
        settings.supabase_jwt_key,
        algorithms=["HS256"],
        audience=JWT_AUDIENCE,
    )
    return payload
