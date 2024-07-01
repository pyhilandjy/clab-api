from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgresql_url: str
    clova_invoke_url: str
    clova_secret: str
    fastapi_name: str
    fastapi_key: str
    aws_access_key_id: str
    aws_secret_access_key: str
    bucket_name: str
    supabase_url: str
    supabase_key: str
    supabase_service_key: str
    supabase_jwt_key: str
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
