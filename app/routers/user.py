import requests
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, Body, Header
from fastapi.responses import FileResponse, StreamingResponse

import supabase
from supabase import create_client, Client

from app.config import settings

router = APIRouter()

# headers = {
#     "apikey": settings.supabase_key,
#     "Authorization": f"Bearer {settings.supabase_key}",
#     "Content-Type": "application/json",
# }

# headers = {"apikey": settings.supabase_key, "Content-Type": "application/json"}

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


# @router.get("/users/")
# async def get_users():
#     response = requests.get(f"{settings.supabase_url}/rest/v1/users", headers=headers)
#     if response.status_code == 200:
#         return response.json()
#     else:
#         return {"error": response.text}


# @router.get("/user")
# async def get_user(authorization: str = Header(None)):
#     if not authorization:
#         raise HTTPException(status_code=401, detail="Authorization header missing")

#     # Supabase 사용자 정보 가져오기
#     user_headers = {**headers, "Authorization": f"Bearer {authorization}"}

#     response = requests.get(
#         f"{settings.supabase_key}/rest/v1/users", headers=user_headers
#     )
#     if response.status_code == 200:
#         return response.json()
#     else:
#         raise HTTPException(status_code=response.status_code, detail=response.text)
