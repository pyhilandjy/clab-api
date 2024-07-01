from typing import Dict
import jwt

from fastapi import APIRouter, HTTPException

from supabase import create_client, Client
from jwt import ExpiredSignatureError, InvalidTokenError, InvalidAudienceError

from app.config import settings

router = APIRouter()

supabase: Client = create_client(settings.supabase_url, settings.supabase_service_key)

JWT_AUDIENCE = "authenticated"


# def get_user_id_from_token(token: str) -> str:
#     try:
#         payload = jwt.decode(token, settings.supabase_jwt_key, algorithms=["HS256"])
#         return payload.get("id")
#     except jwt.PyJWTError:
#         raise HTTPException(status_code=403, detail="Could not validate credentials")


def get_user_info_from_token(token: str) -> str:
    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_key,
            algorithms=["HS256"],
            audience=JWT_AUDIENCE,
        )
        return payload  # "id" 필드에서 사용자 ID를 가져옴
    except ExpiredSignatureError:
        raise ExpiredSignatureError("Token has expired")
    except InvalidTokenError:
        raise InvalidTokenError("Invalid token")
    except InvalidAudienceError:
        raise InvalidAudienceError("Invalid audience")
