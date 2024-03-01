import httpx
import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient
from mock_db import Database
from pydantic_settings import BaseSettings, SettingsConfigDict

from app import parkingbot
from app.config import Settings
from app.services.open_data_parking import OpenDataParking
from app.services.user_manager import UserManager
from app.services.userdata_manager import UserdataManager


class TestSettings(Settings):
    __test__ = False
    model_config = SettingsConfigDict(env_file=".test.env")


@pytest.fixture(scope="session")
def settings() -> BaseSettings:
    return TestSettings()


@pytest.fixture(scope="session")
def fernet(settings) -> Fernet:
    return Fernet(key=settings.FERNET_KEY)


@pytest.fixture(scope="session")
def database() -> Database:
    return Database()


@pytest.fixture(scope="session")
def server(settings) -> TestClient:
    return TestClient(
        app=parkingbot,
        base_url=f"https://127.0.0.1:8000{settings.API_ENDPOINT}",
    )


@pytest.fixture(scope="session")
def open_data(settings) -> OpenDataParking:
    return OpenDataParking(settings, httpx.Client(http2=True))


@pytest.fixture(scope="session")
def user_manager(database, fernet) -> UserManager:
    return UserManager(database, fernet)


@pytest.fixture(scope="session")
def userdata_manager(database, fernet) -> UserdataManager:
    return UserdataManager(database, fernet)
