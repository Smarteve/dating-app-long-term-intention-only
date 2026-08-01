import os
from collections.abc import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.main import create_app


TEST_DATABASE_URL = (
    "postgresql+psycopg://"
    "dating_app_test:dating_app_test@localhost:5433/dating_app_test"
)

# This must happen before importing modules that call get_settings().
os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["IDENTITY_PROVIDER_ISSUER"] = (
    "https://identity-provider.test/auth/v1"
)
os.environ["IDENTITY_PROVIDER_AUDIENCE"] = "authenticated"


@pytest.fixture(scope="session")
def test_engine() -> Generator[Engine, None, None]:
    engine = create_engine(
        TEST_DATABASE_URL,
        pool_pre_ping=True,
    )

    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def db_session(test_engine: Engine) -> Generator[Session, None, None]:
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(
        bind=connection,
        autoflush=False,
        expire_on_commit=False,
    )

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def test_app(db_session: Session) -> Generator[FastAPI, None, None]:
    application = create_app()

    def override_db_session() -> Generator[Session, None, None]:
        yield db_session

    application.dependency_overrides[get_db_session] = override_db_session

    try:
        yield application
    finally:
        application.dependency_overrides.clear()


@pytest.fixture
def client(test_app: FastAPI) -> Generator[TestClient, None, None]:
    with TestClient(test_app) as test_client:
        yield test_client
