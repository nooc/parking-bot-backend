import httpx
import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient
from mock_db import Database
from pydantic_settings import SettingsConfigDict

import app.config
from app import parkingbot
from app.dependencies import get_db, get_fernet
from app.services.gothenburg_open_data import CarParkDataSource
from app.services.history_manager import HistoryManager
from app.services.user_manager import UserManager
from app.services.vehicle_manager import UserdataManager


class TestSettings(app.config.Settings):
    __test__ = False
    model_config = SettingsConfigDict(
        yaml_file="env.pytest.yml", yaml_file_encoding="utf-8", validate_default=False
    )

    HS256_KEY: str
    TEST_TOKEN_INIT: str
    TEST_TOKEN: str
    TEST_TOKEN_INVALID: str


class BearerAuth(httpx.Auth):
    def __init__(self, token) -> None:
        super().__init__()
        self._token = token

    def auth_flow(self, request: httpx.Request):
        request.headers["Authorization"] = f"Bearer {self._token}"
        yield request


@pytest.fixture(scope="session")
def settings() -> TestSettings:
    return TestSettings()


@pytest.fixture(scope="session")
def test_auth_init(settings) -> httpx.Auth:
    return BearerAuth(token=settings.TEST_TOKEN_INIT)


@pytest.fixture(scope="session")
def test_auth(settings) -> httpx.Auth:
    return BearerAuth(token=settings.TEST_TOKEN)


@pytest.fixture(scope="session")
def test_auth_invalid(settings) -> httpx.Auth:
    return BearerAuth(token=settings.TEST_TOKEN_INVALID)


@pytest.fixture(scope="session")
def fernet() -> Fernet:
    return Fernet(key=Fernet.generate_key())


@pytest.fixture(scope="session")
def database(fernet) -> Database:
    return Database(fernet)


@pytest.fixture(scope="session")
def server_with_mock_db(settings, database, fernet) -> TestClient:
    parkingbot.dependency_overrides[get_fernet] = lambda: fernet
    parkingbot.dependency_overrides[get_db] = lambda: database
    return TestClient(
        app=parkingbot,
        base_url=f"https://127.0.0.1:8000{settings.API_ENDPOINT}",
    )


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
def history_manager(database, fernet) -> HistoryManager:
    return HistoryManager(database, fernet)
