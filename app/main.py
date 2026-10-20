"""FastAPI application for the Library Management System API."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import models
from app.config import Settings, StorageBackend
from app.database.session import create_database
from app.in_memory_store import InMemoryStore
from app.models.base import Base
from app.routers.book import router as book_router
from app.routers.members import router as members_router
from app.services.book import DatabaseBookService, InMemoryBookService
from app.services.members import DatabaseMemberService, InMemoryMemberService

# Tag desriptions to organize related operations
tags_metadata = [
    {
        "name": "General",
        "description": "General information about the API"
    },
    {
        "name": "Books",
        "description": "Operations related to books in the library"
    },
    {
        "name": "Members",
        "description": "Operations related to members of the library"
    }
]

@asynccontextmanager
async def lifespan(application: FastAPI):
    """Choose and build the storage-backed services once at startup."""
    settings = Settings()
    application.state.settings = settings
    database = None

    if settings.storage_backend is StorageBackend.MEMORY:
        # Both services must share one store, or a book could never find its member.
        store = InMemoryStore()
        application.state.book_service = InMemoryBookService(store)
        application.state.member_service = InMemoryMemberService(store)
    elif settings.storage_backend is StorageBackend.DATABASE:
        database = create_database(settings)
        Base.metadata.create_all(bind=database.engine)
        application.state.book_service = DatabaseBookService(database.session_factory)
        application.state.member_service = DatabaseMemberService(database.session_factory)

    yield

    # Shutdown: close the connection pool if a database was opened.
    if database is not None:
        database.engine.dispose()

app = FastAPI(
    title="Assignment 2 - Library Management System",
    description="Grant Kostrzewa, SDEV3310-21",
    version="2.0.0",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)

app.include_router(book_router)
app.include_router(members_router)

# GET / endpoint returns a simple message to indicate that the API is running
@app.get("/", tags=["General"], summary="Introduce the API")
def read_root() -> dict[str, str]:
    """Return a short introduction to the API."""
    return {"message": "Welcome to the Library Management System API!"}

# GET /health endpoint returns a simple message to indicate that the API is healthy
@app.get("/health", tags=["General"], summary="Check the health of the API")
def check_health() -> dict[str, str]:
    """Return a simple message to indicate that the API is healthy."""
    return {"status": "API is healthy!"}