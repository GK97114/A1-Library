"""Shared pytest fixtures for integration and API tests."""

import os
from collections.abc import Generator

import pytest
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from starlette.testclient import TestClient
from testcontainers.community.postgres import PostgresContainer

from app.auth.users import UserRole, get_token_for_role
from app.config import Settings, StorageBackend

@pytest.fixture(scope="session")
def postgres_test_container() -> Generator[PostgresContainer, None, None]:
    """Start a disposable PostgreSQL database for the entire pytest session."""
    original_database_url = os.environ.get("DATABASE_URL")
    original_storage_backend = os.environ.get("STORAGE_BACKEND")
    try:
        with PostgresContainer(
            "postgres:17.2",
            username="postgres",
            password="postgres",
            dbname="library_test",
            driver="psycopg",
        ) as container:
            os.environ["DATABASE_URL"] = container.get_connection_url()
            os.environ["STORAGE_BACKEND"] = "database"
            yield container
    finally:
        if original_database_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = original_database_url
        if original_storage_backend is None:
            os.environ.pop("STORAGE_BACKEND", None)
        else:
            os.environ["STORAGE_BACKEND"] = original_storage_backend

@pytest.fixture(scope="session")
def db_engine(postgres_test_container: PostgresContainer) -> Generator[Engine, None, None]:
    """Return the app engine configured for the temporary PostgreSQL container."""
    from app import models
    from app.config import Settings
    from app.database.session import create_database

    database = create_database(Settings())
    try:
        yield database.engine
    finally:
        database.engine.dispose()

@pytest.fixture
def reset_database(db_engine: Engine) -> Generator[None, None, None]:
    """Give each test a clean database by dropping and recreating all tables."""
    from app.models.base import Base

    Base.metadata.drop_all(bind=db_engine)
    Base.metadata.create_all(bind=db_engine)
    try:
        yield
    finally:
        Base.metadata.drop_all(bind=db_engine)


@pytest.fixture
def database_session_factory(
    reset_database: None, db_engine: Engine
) -> sessionmaker[Session]:
    """Provide a session factory for each repository integration test."""
    return sessionmaker(bind=db_engine, autoflush=False, expire_on_commit=False)


@pytest.fixture
def database_api_client(reset_database: None) -> Generator[TestClient, None, None]:
    """Provide a TestClient connected to the temporary database."""
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def memory_api_client(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[TestClient, None, None]:
    """Provide a TestClient for in-memory backend services."""
    monkeypatch.setenv("STORAGE_BACKEND", "memory")

    from app.main import app
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def default_settings() -> Settings:
    """Return a Settings object with the default configuration for testing."""
    return Settings(storage_backend=StorageBackend.MEMORY)

@pytest.fixture
def member_headers(default_settings: Settings) -> dict[str, str]:
    """Provide the auth header for the default member token."""
    return {
        "Authorization": f"Bearer {get_token_for_role(UserRole.MEMBER, default_settings)}"
    }

@pytest.fixture
def admin_headers(default_settings: Settings) -> dict[str, str]:
    """Provide the auth header for the default admin token."""
    return {
        "Authorization": f"Bearer {get_token_for_role(UserRole.ADMIN, default_settings)}"
    }

@pytest.fixture
def member_api_client(
    database_api_client: TestClient,
    member_headers: dict[str, str],
) -> TestClient:
    """Provide the per-test API client configured as a member user."""
    database_api_client.headers.update(member_headers)
    return database_api_client

@pytest.fixture
def admin_api_client(
    database_api_client: TestClient,
    admin_headers: dict[str, str],
) -> TestClient:
    """Provide the per-test API client configured as an admin user."""
    database_api_client.headers.update(admin_headers)
    return database_api_client