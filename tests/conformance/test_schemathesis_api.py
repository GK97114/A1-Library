"""Schemathesis-generated checks for safe API operations."""

import pytest
import schemathesis
from hypothesis import HealthCheck, settings
from schemathesis.checks import allow_header_conformance
from starlette.testclient import TestClient

from app.main import app


@pytest.fixture
def api_schema(memory_api_client: TestClient) -> schemathesis.schemas.BaseSchema:
    """Load the OpenAPI schema after the in-memory app has started."""
    return schemathesis.openapi.from_asgi("/openapi.json", app)


schema = schemathesis.pytest.from_fixture("api_schema").include(method="GET")


@schema.parametrize()
@settings(
    max_examples=5,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
def test_schemathesis_safe_api_operations_match_openapi_contract(
    case,
    admin_headers: dict[str, str],
) -> None:
    """Run generated read-only requests and validate responses against OpenAPI."""
    case.call_and_validate(
        headers=admin_headers,
        excluded_checks=[allow_header_conformance],
    )
