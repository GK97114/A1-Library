from fastapi import FastAPI

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