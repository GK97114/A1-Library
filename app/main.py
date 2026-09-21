from fastapi import FastAPI

from app.routers import book, members

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

app = FastAPI(
    title="Assignment 1 - Library Management System",
    description="Grant Kostrzewa, SDEV3310-21",
    version="1.0.0",
    openapi_tags=tags_metadata
)

app.include_router(book.router)
app.include_router(members.router)

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