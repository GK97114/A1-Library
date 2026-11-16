"""Shared pytest intergration fixtures for API tests."""

import os
from collections.abc import Generator

import pytest
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from starlette.testclient import TestClient
from testcontainers.postgres import PostgresContainer

from app.auth.users import UserRole, get_token_for_role
from app.config import Settings, StorageBackend

# postgres_container
#   Start a disposable PostgreSQL container for the test; yield only its
#   connection URL and stop/remove it during fixture teardown.
@pytest.fixture(scope="session")
def postgres_test_container() -> Generator[str, None, None]:
    """Start a disposable PostgreSQL database for the entire pytest session."""
    with PostgresContainer(
        "postgres:17.2",
        username="postgres",
        password="postgres",
        dbname="library_test",
        driver="psycopg",
    ) as container:
        os.environ["DATABASE_URL"] = container.get_connection_url()
        yield container
    os.environ.pop("DATABASE_URL", None)

@pytest.fixture(scope="session")
def db_engine(postgres_test_container: PostgresContainer) -> Engine:
    """Return the app engine configured for the temporary PostgreSQL container."""
    from app import models
    from app.config import Settings
    from app.database.session import create_database

    return create_database(Settings()).engine

@pytest.fixture
def reset_database(db_engine: Engine) -> Generator[None, None, None]:
    """Give each test a clean database by dropping and recreating all tables."""
    from app.models.base import Base

    # Drop all tables and recreate them before each test, then drop them again after the test.
    Base.metadata.drop_all(bind=db_engine)
    Base.metadata.create_all(bind=db_engine)

    # Yield control to the test function, then drop all tables again after the test completes.
    yield
    Base.metadata.drop_all(bind=db_engine)


@pytest.fixture(scope="session")
def database_session_factory(
    reset_database: None, db_engine: Engine
) -> Generator[Session, None, None]:
    """Provide a SQLAlchemy session for repository integration tests."""
    session_factory = sessionmaker(bind=db_engine, autoflush=False)
    with session_factory() as session:
        # Yield the session to the test function, then rollback any changes after the test completes.
        yield session
        session.rollback()


@pytest.fixture
def database_api_client(reset_database: None) -> Generator[TestClient, None, None]:
    """Provide a TestClient after the temporary db is ready"""
    from app.main import app
    with TestClient(app) as test_clinet:
        yield test_clinet


@pytest.fixture
def memory_api_client(monkeypatch: pytest.MonkeyPatch,) -> Generator[TestClient, None, None]:
    """Provide a TestClient for in-memory backend services."""
    monkeypatch.setenv("STORAGE_BACKEND", "memory")
    monkeypatch.delenv("DATABASE_URL", raising=False)

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
    """Provide the per-test API client configed as a member user."""
    database_api_client.headers.update(member_headers)
    return database_api_client

@pytest.fixture
def admin_api_client(
    database_api_client: TestClient,
    admin_headers: dict[str, str],
) -> TestClient:
    """Provide the per-test API client configed as an admin user."""
    database_api_client.headers.update(admin_headers)
    return database_api_client