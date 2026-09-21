# Assignment 1 - Library Management System

A FastAPI application for managing books and library members. The API uses
Pydantic models for request and response validation and temporary in-memory
storage for the current assignment.

## Requirements

- Python 3.10 or newer
- FastAPI
- Uvicorn
- Pydantic
- `email-validator` for Pydantic's `EmailStr` field

## Set Up the Project

Open a terminal in the project root:

```powershell
cd "C:\path\to\A1-Library"
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install fastapi "uvicorn[standard]" pydantic email-validator
```

To record the installed packages for another environment:

```powershell
python -m pip freeze > requirements.txt
```

## Run the API

From the project root, with the virtual environment activated:

```powershell
python -m uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`.

Interactive API documentation is available at:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

Stop the development server with `Ctrl+C`.

## API Endpoints

### General

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/` | Confirm that the API is running |
| GET | `/health` | Check API health |

### Books

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/books` | List all books |
| GET | `/books/{book_id}` | Get one book by ID |
| POST | `/books` | Create a book |
| PUT | `/books/{book_id}` | Replace a book |
| DELETE | `/books/{book_id}` | Delete a book |

Book request fields:

- `title`: required string, 1-200 characters
- `BookAuthor`: required string, 1-120 characters
- `Bookisbn`: required string, 10-17 characters
- `published_year`: required integer from 1450 through the current year
- `member_id`: optional integer identifying the borrowing member

Example book request:

```json
{
	"title": "The Hobbit",
	"BookAuthor": "J.R.R. Tolkien",
	"Bookisbn": "978-0547928227",
	"published_year": 1937,
	"member_id": null
}
```

### Members

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/members` | List all members |
| GET | `/members/{member_id}` | Get one member by ID |
| POST | `/members` | Create a member |
| PUT | `/members/{member_id}` | Replace a member |
| DELETE | `/members/{member_id}` | Delete a member |
| GET | `/members/{member_id}/books` | List books borrowed by a member |

Member request fields:

- `name`: required string, 1-120 characters
- `email`: required valid email address
- `memberships_id`: required membership identifier
- `phone`: required in `(###)-###-####` format

Example member request:

```json
{
	"name": "Jane Doe",
	"email": "jane.doe@example.com",
	"memberships_id": "CCCCL-0002",
	"phone": "(555)-123-4567"
}
```

Successful creates return `201 Created`. Missing or invalid fields return
`422 Unprocessable Entity`. Requests for missing records return `404 Not
Found`. A book or member involved in an active borrowing relationship cannot
be deleted and returns `409 Conflict`.

## Storage Notes

The application currently stores books and members in Python lists in
`app/storage.py`. Data is temporary and is reset whenever the application
restarts. The API currently generates integer IDs from the highest existing
ID in each list.

## Project Structure

```text
A1-Library/
├── app/
│   ├── main.py                 # FastAPI application and general endpoints
│   ├── storage.py              # Temporary in-memory book and member data
│   ├── routers/
│   │   ├── book.py             # Book endpoints
│   │   └── members.py          # Member endpoints
│   └── schemas/
│       ├── book.py             # Book Pydantic models
│       └── members.py          # Member Pydantic models
├── .venv/                      # Local virtual environment, if created
├── .gitignore
└── README.md
```