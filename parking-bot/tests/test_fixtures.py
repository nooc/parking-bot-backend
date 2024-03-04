import httpx
import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient
from mock_db import Database
from pydantic_settings import SettingsConfigDict

from app import parkingbot
from app.config import Settings
from app.services.carpark_data import CarParkDataSource
from app.services.log_manager import ParkingLogManager
from app.services.user_manager import UserManager
from app.services.userdata_manager import UserdataManager


class TestSettings(Settings):
    __test__ = False
    model_config = SettingsConfigDict(env_file=".test.env")

    TEST_HS256_KEY: str = b"F)5<{Ab*JaIH+I9L>b!i%VZkUBc`+hS-"


@pytest.fixture(scope="session")
def settings() -> TestSettings:
    return TestSettings()


@pytest.fixture(scope="session")
def fernet(settings) -> Fernet:
    return Fernet(key=settings.FERNET_KEY)


@pytest.fixture(scope="session")
def database(fernet) -> Database:
    return Database(fernet)


@pytest.fixture(scope="session")
def server(settings) -> TestClient:
    return TestClient(
        app=parkingbot,
        base_url=f"https://127.0.0.1:8000{settings.API_ENDPOINT}",
    )


@pytest.fixture(scope="session")
def parking_data(settings) -> CarParkDataSource:
    return CarParkDataSource(settings, httpx.Client(http2=True))


@pytest.fixture(scope="session")
def user_manager(database, fernet) -> UserManager:
    return UserManager(database, fernet)


@pytest.fixture(scope="session")
def userdata_manager(database, fernet) -> UserdataManager:
    return UserdataManager(database, fernet)


@pytest.fixture(scope="session")
def log_manager(database, fernet) -> ParkingLogManager:
    return ParkingLogManager(database, fernet)
