from typing import Optional

from pydantic import AnyHttpUrl, EmailStr, Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        yaml_file="env.prod.yml", yaml_file_encoding="utf-8", validate_default=False
    )

    DEBUG: bool = False
    SWAGGER_UI: bool = False

    PROJECT_NAME: str
    PROJECT_DESC: str = ""
    APP_URL: AnyHttpUrl = None
    APP_CALLBACK_SCHEME: str
    API_ENDPOINT: str

    RSA_PRIV_SERVER: str
    RSA_PUB_APP: str

    SERVER_NAME: str

    # App engien env
    GOOGLE_CLOUD_PROJECT: str
    GAE_APPLICATION: str
    GAE_DEPLOYMENT_ID: str
    GAE_INSTANCE: str
    GAE_REGION: str

    CREDENTIALS_JSON: str
    STORAGE_BUCKET: str
    TASK_QUEUE_NAME: str

    SMTP_TLS: bool = True
    SMTP_PORT: int = 25
    SMTP_HOST: str = None
    SMTP_USER: str = None
    SMTP_PASSWORD: str = None
    SMTP_FROM_EMAIL: EmailStr = None
    SMTP_FROM_NAME: str = None

    GBG_DATA_APP_ID: str
    GBG_DATA_BASE_URL: AnyHttpUrl
    GBG_DATA_TOLL_LIST: str
    GBG_DATA_TOLL_ITEM: str
    GBG_DATA_FREE_LIST: str
    GBG_DATA_FREE_ITEM: str
    GBG_PARKING_KIOSK_INFO_URL: AnyHttpUrl

    FERNET_KEY: str = None
    HS256_KEY: str = None
    JWT_ISSUER: str = "parkingbot"
    JWT_AUDIENCE: str = "parkingbot"
    JWT_EXP_DAYS: int = 1

    DGGS_CELL_EXPIRY_DAYS: int = 50

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return YamlConfigSettingsSource(settings_cls=settings_cls), env_settings


conf = Settings()

__all__ = ("Settings", "conf")
