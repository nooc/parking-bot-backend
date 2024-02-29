import httpx
import pytest
from fastapi.testclient import TestClient
from pydantic_settings import BaseSettings, SettingsConfigDict

from app import parkingbot
from app.config import Settings
from app.services.open_data_parking import OpenDataParking


class TestSettings(Settings):
    __test__ = False
    model_config = SettingsConfigDict(env_file=".test.env")


@pytest.fixture(scope="session")
def settings() -> BaseSettings:
    return TestSettings()


@pytest.fixture(scope="session")
def server(settings) -> TestClient:
    return TestClient(
        app=parkingbot,
        base_url=f"https://127.0.0.1:8000{settings.API_ENDPOINT}",
    )


@pytest.fixture(scope="session")
def open_data(settings) -> OpenDataParking:
    return OpenDataParking(settings, httpx.Client(http2=True))
