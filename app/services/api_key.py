from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN

from app.config import settings


class ApiKey:
    FASTAPI_KEY_NAME = settings.fastapi_name
    FASTAPI_KEY = settings.fastapi_key


api_key_header = APIKeyHeader(name=ApiKey.FASTAPI_KEY_NAME, auto_error=False)


async def get_api_key(fastapi_key: str = Security(api_key_header)):
    if fastapi_key == ApiKey.FASTAPI_KEY:
        return fastapi_key
    else:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid API Key")
