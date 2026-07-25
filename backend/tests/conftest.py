import os
from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session


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