# Assignment 2 - Library Management System With Database

A FastAPI application for managing books and library members. Request and
response validation uses Pydantic models. Data can be stored either in
process memory (temporary) or in a PostgreSQL database (persistent), and the
backend is chosen with a single setting.

## Prerequisites

- Python 3.11 or newer
- [`uv`](https://docs.astral.sh/uv/) for Python project and dependency management
- Docker Desktop, to run PostgreSQL locally

## Set Up the Project

Open PowerShell in the project root. If you are starting from another
directory, change to the project directory:

```powershell
cd "C:\path\to\project"
```

Create the local environment and install the locked project dependencies:

```powershell
uv sync
```

`uv sync` uses `pyproject.toml` and `uv.lock` to install the project and its
dependencies into `.venv`. You do not need to activate that environment when
using `uv run`.

## Configure the Application

Create your local `.env` file from the safe example, then edit the placeholders
with values you choose:

```powershell
Copy-Item .env.example .env
```

The `.env` file is ignored by Git. Keep real credentials there and do not
commit them. Docker Compose reads `POSTGRES_USER`, `POSTGRES_PASSWORD`, and
`POSTGRES_DB` from this file to initialize PostgreSQL. The API reads
`STORAGE_BACKEND`, `DATABASE_URL`, and `DATABASE_ECHO_SQL`.

| Variable | Purpose |
| --- | --- |
| `STORAGE_BACKEND` | `database` selects PostgreSQL (the default); `memory` selects temporary process-local storage |
| `DATABASE_URL` | SQLAlchemy connection URL; required when the backend is `database` |
| `DATABASE_ECHO_SQL` | Optional. Set to `true` to log SQL statements during development |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Credentials and database name used by Docker Compose |

The Docker container publishes PostgreSQL on host port `5434` (container port
`5432`). The `DATABASE_URL` in `.env` must connect to `localhost:5434` and use
the same user, password, and database name as the `POSTGRES_*` settings. Use a
SQLAlchemy Psycopg URL and replace its placeholders with your local values:

```text
DATABASE_URL=postgresql+psycopg://your_db_user:your_db_password@localhost:5434/your_db_name
```

If `STORAGE_BACKEND` is `database` and `DATABASE_URL` is missing, the
application refuses to start and reports the missing setting.

## Start the Database

Start Docker Desktop, then run these commands from the project root:

```powershell
docker compose up -d
docker compose ps
```

`docker compose up -d` starts PostgreSQL; it does not start the API. The API
creates the `members` and `book` tables when it starts with
`STORAGE_BACKEND=database`. Table creation only adds missing tables; it does not
insert sample data or migrate existing tables after model changes.

PostgreSQL data is stored in the named `pgdata` Docker volume. Stopping and
restarting the container preserves that data. To stop the container while
keeping its data, run `docker compose down`. To remove the database volume and
all its data as well, run `docker compose down -v`; only do this when you
intentionally want a fresh database.

## Run the API

After configuring `.env` and starting PostgreSQL, run the API from the project
root:

```powershell
uv run uvicorn app.main:app --reload
```

The API listens at `http://127.0.0.1:8000`. Stop the development server with
`Ctrl+C`.

Interactive API documentation is available at:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

Use `GET /members` or `GET /books` to check the API's data endpoints. A new
database will return empty lists until records are created. You can create
related member and book records using the example requests in the API section
below. `/health` reports API health but does not check the database connection.

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
│   ├── main.py                 # FastAPI app and startup/shutdown wiring
│   ├── config.py               # Validated settings and backend selection
│   ├── exceptions.py           # Domain errors raised by services
│   ├── dependencies.py         # Gives routers the startup-selected services
│   ├── in_memory_store.py      # Shared lists used by the in-memory services
│   ├── database/
│   │   └── session.py          # Engine and session factory
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── base.py
│   │   ├── __init__.py
│   │   ├── book.py
│   │   └── members.py
│   ├── repositories/           # SQL queries used by the database services
│   │   ├── book.py
│   │   └── members.py
│   ├── routers/                # HTTP endpoints
│   │   ├── book.py
│   │   ├── http_errors.py      # Translate application errors to HTTP errors
│   │   └── members.py
│   ├── schemas/                # Pydantic request and response models
│   │   ├── book.py
│   │   └── members.py
│   └── services/
│       ├── book/
│       │   ├── base.py         # BookService abstraction
│       │   ├── database.py     # PostgreSQL implementation
│       │   └── in_memory.py    # In-memory implementation
│       └── members/
│           ├── base.py         # MemberService abstraction
│           ├── database.py     # PostgreSQL implementation
│           └── in_memory.py    # In-memory implementation
├── docker-compose.yml          # PostgreSQL container
├── pyproject.toml              # Project metadata and dependencies
├── uv.lock                     # Locked dependency versions
├── .env.example                # Template for local settings
├── .gitignore
└── README.md
```