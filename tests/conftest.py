# Planned shared integration fixtures (implement only with Testcontainers).
#
# postgres_container
#   Start a disposable PostgreSQL container for the test; yield only its
#   connection URL and stop/remove it during fixture teardown.
#
# database_session_factory
#   Build an engine/session factory from the container URL, create the real
#   Base.metadata tables, yield the factory, then drop tables and dispose the
#   engine. Never read or connect to a developer's local Library database.
#
# database_api_client
#   Configure the API to use the container URL and database backend, enter
#   TestClient as a context manager so lifespan startup/shutdown runs, and
#   provide fresh database state for each test.
#
# memory_api_client
#   Configure a fresh in-memory application per test and enter TestClient as a
#   context manager so no state is shared between tests.
#
# Keep container and environment overrides fixture-scoped so failures do not
# leak settings, database state, or containers into other tests.
