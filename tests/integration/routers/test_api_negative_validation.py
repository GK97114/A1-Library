# Planned HTTP negative tests for request validation using FastAPI TestClient.
#
# Use a fresh memory_api_client or database_api_client per test and provide a
# valid admin_headers token for protected write routes. For database-client
# cases, rely on the disposable Testcontainers PostgreSQL fixture only.
#
# test_api_rejects_each_missing_required_book_field
#   Send otherwise-valid POST /books bodies missing title, author, isbn,
#   published_year, or member_id in turn; assert HTTP 422 and the documented
#   HTTPValidationError body shape, not merely a non-success status.
#
# test_api_rejects_unknown_book_fields
#   Send a valid Book body with an unrecognized key; assert HTTP 422 and check
#   the validation error identifies the extra field.
#
# test_api_rejects_book_field_values_outside_schema_boundaries
#   Check title over 200 characters, author over 120, ISBN shorter than 10 or
#   longer than 17, published_year below 1450 or after the current year, and
#   member_id at zero or below. Assert HTTP 422 and a validation-error body
#   matching the documented response schema.
#
# test_api_rejects_each_missing_required_member_field
#   Send otherwise-valid POST /members bodies missing name, email,
#   membership_id, or phone; assert HTTP 422 and the documented validation
#   response shape.
#
# test_api_rejects_unknown_member_fields
#   Send a valid Member body with an unrecognized key; assert HTTP 422 and check
#   the validation error identifies the extra field.
#
# test_api_rejects_member_values_outside_schema_boundaries
#   Check name over 120 characters, membership_id over 20 characters, malformed
#   or over-100-character email, and phone values outside (###)-###-####.
#   Assert HTTP 422 and validate the body against the documented
#   HTTPValidationError response schema.
#
# test_api_rejects_invalid_book_and_member_path_id_types
#   Send a non-integer ID to representative GET/PUT/DELETE paths such as
#   /books/not-an-id and /members/not-an-id; authenticate protected requests,
#   assert HTTP 422, and check the response's validation-error shape matches
#   the operation's OpenAPI 422 schema.
#
# Keep boundary expectations in sync with the Pydantic rules: membership_id
# currently has a maximum but no minimum, and ISBN has length rules but no
# checksum rule.
