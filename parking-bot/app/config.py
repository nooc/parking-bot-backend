from typing import Optional

from pydantic import AnyHttpUrl, EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".prod.env")

    DEBUG: Optional[bool] = False
    SWAGGER_UI = Optional[bool] = False

    PROJECT_NAME: Optional[str] = None
    PROJECT_DESC: Optional[str] = None
    APP_URL: Optional[AnyHttpUrl] = None
    APP_CALLBACK_SCHEME: Optional[str] = None
    API_ENDPOINT: Optional[str] = None

    RSA_PRIV_SERVER: Optional[str] = None
    RSA_PUB_APP: Optional[str] = None

    SERVER_NAME: Optional[str] = None
    GOOGLE_CLOUD_PROJECT: Optional[str] = None
    GAE_APPLICATION: Optional[str] = None
    GAE_DEPLOYMENT_ID: Optional[str] = None
    GAE_INSTANCE: Optional[str] = None
    TASK_QUEUE_NAME: Optional[str] = None
    GAE_REGION: Optional[str] = None
    CREDENTIALS_JSON: Optional[str] = None
    STORAGE_BUCKET: str

    SMTP_TLS: Optional[bool] = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: EmailStr
    SMTP_FROM_NAME: str

    GBG_DATA_APP_ID: str
    GBG_DATA_BASE_URL: AnyHttpUrl
    GBG_DATA_TOLL_LIST: str
    GBG_DATA_TOLL_ITEM: str
    GBG_DATA_FREE_LIST: str
    GBG_DATA_FREE_ITEM: str
    GBG_PARKING_KIOSK_INFO_URL: AnyHttpUrl

    FERNET_KEY: bytes


conf = Settings()

__all__ = ("Settings", "conf")
