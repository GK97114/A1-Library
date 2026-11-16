# Planned conformance tests for the published OpenAPI security contract.
#
# test_openapi_declares_the_bearer_auth_scheme
#   Check components.securitySchemes contains BearerAuth as HTTP bearer auth.
#
# test_openapi_marks_only_protected_operations_with_bearer_security
#   Check public GET / and GET /health have no security requirement; check
#   protected Book/Member operations declare the BearerAuth requirement.
#
# test_openapi_marks_mutating_operations_as_admin_protected
#   Check Book and Member POST, PUT, and DELETE operations carry the same bearer
#   security requirement as protected reads; role enforcement is covered by
#   authentication/authorization tests, not inferable from OpenAPI security.
#
# test_openapi_publishes_expected_authentication_error_responses
#   Check the documented 401 and 403 responses where the API contract promises
#   them, and compare the published contract with actual protected routes.
