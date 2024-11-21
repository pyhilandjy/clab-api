from typing import Dict
from fastapi import Header, Security, APIRouter
from fastapi.security.api_key import APIKeyHeader
import jwt
from supabase import Client, create_client

from app.config import settings

api_key_header = APIKeyHeader(name="authorization", auto_error=False)

supabase: Client = create_client(settings.supabase_url, settings.supabase_service_key)

JWT_AUDIENCE = "authenticated"

router = APIRouter()


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


@router.get("/users/{user_id}", tags=["users"])
def get_user(user_id: str):
    try:
        response = supabase.auth.admin.get_user_by_id(user_id)
        user = response.user
        user_info = {
            "id": user.id,
            "name": user.user_metadata.get("name", ""),
            "email": user.email,
        }

        return user_info
    except Exception as e:
        return {"error": str(e)}


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
