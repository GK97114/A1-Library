# Assignment 2 - Library Management System With Database

A FastAPI application for managing books and library members. Request and
response validation uses Pydantic models. Data can be stored either in
process memory (temporary) or in a PostgreSQL database (persistent), and the
backend is chosen with a single setting.

## Project Status (checkpoint)

Remove this section once everything is working.

- [x] Assignment 1 feedback fixes (field names, required `member_id`, duplicate checks)
- [x] Settings and backend selection (`config.py`)
- [x] PostgreSQL in Docker (`docker-compose.yml`)
- [x] ORM models, repositories, in-memory store
- [x] Book service: abstract contract, in-memory and database implementations
- [x] Member service (contract and both implementations)
- [x] Database engine and session factory (`app/database/session.py`)
- [x] Application startup wiring (`main.py` lifespan, `dependencies.py`)
- [x] Routers converted from lists to services
- [ ] Testing against both backends, including restart persistence

## Requirements

- Python 3.11 or newer (the settings use `enum.StrEnum`)
- Docker Desktop, for the PostgreSQL container
- Python packages:
  - FastAPI and Uvicorn
  - Pydantic and `pydantic-settings`
  - `email-validator` for Pydantic's `EmailStr` field
  - SQLAlchemy 2.x
  - Psycopg 3 (`psycopg[binary]`)

## Set Up the Project

Open a terminal in the project root:

```powershell
cd "C:\path\to\project"
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install fastapi "uvicorn[standard]" pydantic pydantic-settings email-validator "sqlalchemy>=2.0" "psycopg[binary]"
```

To record the installed packages for another environment:

```powershell
python -m pip freeze > requirements.txt
```

## Configure the Application

Copy `.env.example` to `.env` and fill in your own values. `.env` is ignored by
Git and must never be committed.

| Variable | Purpose |
| --- | --- |
| `STORAGE_BACKEND` | `memory` for temporary storage or `database` for PostgreSQL |
| `DATABASE_URL` | SQLAlchemy URL, required only when the backend is `database` |
| `DATABASE_ECHO_SQL` | Optional. `true` prints every SQL statement |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Used by Docker Compose to create the database |

The Docker container publishes PostgreSQL on host port `5433`, so the URL in
`.env` must use that port:

```text
DATABASE_URL=postgresql+psycopg://your_db_user:your_db_password@localhost:5433/your_db_name
```

If `STORAGE_BACKEND` is `database` and `DATABASE_URL` is missing, the
application refuses to start and reports the missing setting.

## Start the Database

Start Docker Desktop, then from the project root:

```powershell
docker compose up -d     # start PostgreSQL in the background
docker compose ps        # confirm library-db is running
docker compose down      # stop it, keeping the data
docker compose down -v   # stop it and delete all data (fresh start)
```

Tables are created automatically at application startup when the database
backend is selected. Data is stored in a named Docker volume, so it survives
stopping and restarting both the container and the API.

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

## Architecture

The application is split into layers. Routers handle HTTP, schemas validate
requests, services hold the business rules, and the storage backend is chosen
once at startup.

```mermaid
flowchart TD
    Client([HTTP client]) --> Router[Routers]
    Router -->|Depends| Dep[dependencies.py]
    Dep -->|reads app.state| Contract["BookService / MemberService<br/>(abstract contracts)"]
    Main[main.py lifespan] -->|builds once at startup| Contract
    Contract -.->|STORAGE_BACKEND=memory| Mem[In-memory services]
    Contract -.->|STORAGE_BACKEND=database| Db[Database services]
    Mem --> Store[InMemoryStore]
    Db --> Repo[Repositories]
    Repo --> Pg[(PostgreSQL)]
    Store --> Models[ORM models]
    Repo --> Models
```

Each service is an abstract base class with two implementations. The routers
depend only on the abstract type, so they never know which backend is running.

```mermaid
classDiagram
    class BookService {
        <<abstract>>
        list_books()
        get_book(book_id)
        create_book(data)
        replace_book(book_id, data)
        delete_book(book_id)
    }
    class MemberService {
        <<abstract>>
        list_members()
        get_member(member_id)
        create_member(data)
        replace_member(member_id, data)
        delete_member(member_id)
        list_member_books(member_id)
    }
    BookService <|-- InMemoryBookService
    BookService <|-- DatabaseBookService
    MemberService <|-- InMemoryMemberService
    MemberService <|-- DatabaseMemberService
    InMemoryBookService --> InMemoryStore : uses
    InMemoryMemberService --> InMemoryStore : uses
    DatabaseBookService --> BookRepository : uses
    DatabaseBookService --> MemberRepository : checks member
    DatabaseMemberService --> MemberRepository : uses
    DatabaseMemberService --> BookRepository : checks books
```

### Database model

One member can have many books. Each book must reference an existing member
through a non-null foreign key. PostgreSQL generates the primary keys, and the
database enforces the unique constraints.

```mermaid
erDiagram
    MEMBERS ||--o{ BOOKS : "has many"
    MEMBERS {
        int id PK
        string name "NOT NULL"
        string email UK "NOT NULL"
        string membership_id UK "NOT NULL"
        string phone "NOT NULL"
    }
    BOOKS {
        int id PK
        string title "NOT NULL"
        string author "NOT NULL"
        string isbn UK "NOT NULL"
        int published_year "NOT NULL"
        int member_id FK "NOT NULL"
    }
```

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
- `author`: required string, 1-120 characters
- `isbn`: required string, 10-17 characters, must be unique (hyphens and
  spaces are ignored when checking for duplicates)
- `published_year`: required integer from 1450 through the current year
- `member_id`: required positive integer that must identify an existing member

Example book request:

```json
{
  "title": "The Hobbit",
  "author": "J.R.R. Tolkien",
  "isbn": "978-0547928227",
  "published_year": 1937,
  "member_id": 1
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
- `email`: required valid email address, must be unique (case-insensitive)
- `membership_id`: required membership identifier, must be unique
  (case-insensitive)
- `phone`: required in `(###)-###-####` format

Example member request:

```json
{
  "name": "Jane Doe",
  "email": "jane.doe@example.com",
  "membership_id": "CCCCL-0002",
  "phone": "(555)-123-4567"
}
```

## Response Codes and Business Rules

| Code | Meaning |
| --- | --- |
| `201 Created` | A book or member was created |
| `204 No Content` | A book or member was deleted |
| `404 Not Found` | The requested record does not exist, including a book request whose `member_id` does not match an existing member |
| `409 Conflict` | A duplicate ISBN, member email, or membership ID, or an attempt to delete a member who still has books |
| `422 Unprocessable Entity` | A required field is missing or invalid |

Rules that apply to both storage backends:

- Every book must reference an existing member, both when it is created and
  when it is replaced.
- A book can be deleted at any time.
- A member who still has books cannot be deleted.
- Error responses describe the problem without exposing database internals.

## Storage Backends

| Backend | Setting | Behavior |
| --- | --- | --- |
| In-memory | `STORAGE_BACKEND=memory` | Data lives in Python lists inside one shared `InMemoryStore`. It is temporary and resets whenever the application restarts. The application assigns integer IDs. |
| PostgreSQL | `STORAGE_BACKEND=database` | Data is stored in PostgreSQL through SQLAlchemy and survives restarts. PostgreSQL generates the IDs. |

The backend is selected once when the application starts. Both backends follow
the same abstract service contract and raise the same domain errors.

## Project Structure

```text
project-root/
├── app/
│   ├── main.py                 # FastAPI app, startup wiring, error handlers
│   ├── config.py               # Validated settings and backend selection
│   ├── exceptions.py           # Domain errors raised by services
│   ├── dependencies.py         # Gives routers the startup-selected services
│   ├── in_memory_store.py      # Shared lists used by the in-memory services
│   ├── database/
│   │   └── session.py          # Engine and session factory
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── base.py
│   │   ├── book.py
│   │   └── members.py
│   ├── repositories/           # SQL queries used by the database services
│   │   ├── book.py
│   │   └── members.py
│   ├── routers/                # HTTP endpoints
│   │   ├── book.py
│   │   └── members.py
│   ├── schemas/                # Pydantic request and response models
│   │   ├── book.py
│   │   └── members.py
│   └── services/               # Business rules and storage choice
│       ├── book/               # BookService contract + two implementations
│       └── members/            # MemberService contract + two implementations
├── docker-compose.yml          # PostgreSQL container
├── .env.example                # Template for local settings
├── .gitignore
└── README.md
```