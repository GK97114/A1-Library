# Planned Schemathesis-generated API contract checks.
#
# test_schemathesis_safe_api_operations_match_openapi_contract
#   Build the Schemathesis schema from the running app's generated OpenAPI
#   document and run selected safe operations through the in-process ASGI app.
#
# Select public GET / and GET /health plus protected read-only GET operations
# (for example GET /books, GET /members, and item/related-book reads). Exclude
# POST, PUT, and DELETE so generated cases cannot mutate API state.
#
# Supply the configured admin or member bearer token for protected GET
# operations. Confirm generated requests include authentication where required
# and that missing/invalid authentication behavior remains covered by the
# explicit authentication tests.
#
# Validate every generated response against its documented status, headers,
# content type, and response schema. Include documented not-found and 422
# outcomes when those are generated, but keep generated inputs bounded to the
# selected safe operations and available TestClient/ASGI transport.
#
# Schemathesis is not currently listed in the project dependencies; add it as
# a development dependency when implementing this test, then document the
# focused and full-suite commands in README.md.
