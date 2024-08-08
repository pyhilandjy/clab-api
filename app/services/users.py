from typing import Dict
from fastapi.security.api_key import APIKeyHeader
import jwt
from fastapi import APIRouter, Header, Security
from supabase import Client, create_client

from app.config import settings

router = APIRouter()
api_key_header = APIKeyHeader(name="authorization", auto_error=False)
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


async def get_current_user(authorization: str = Security(api_key_header)):
    try:
        token = authorization.split(" ")[1]
        payload = get_user_info_from_token(token)
        return payload
    except Exception as e:
        raise e
