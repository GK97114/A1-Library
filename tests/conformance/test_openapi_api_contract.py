# Planned conformance tests for the generated OpenAPI document.
#
# test_generated_openapi_document_passes_spec_validator
#   Obtain the document from app.openapi() and validate it with an OpenAPI
#   specification validator against the OpenAPI version the application emits.
#
# test_openapi_publishes_book_operations_and_schemas
#   Check GET /books and GET /books/{book_id} return BookResponse schemas, POST
#   /books accepts BookCreate and returns BookResponse, PUT /books/{book_id}
#   accepts BookUpdate and returns BookResponse, and DELETE /books/{book_id}
#   documents its no-content success response.
#
# test_openapi_publishes_member_operations_and_schemas
#   Check GET /members and GET /members/{member_id} return MemberResponse
#   schemas, POST /members accepts MemberCreate and returns MemberResponse,
#   PUT /members/{member_id} accepts MemberUpdate and returns MemberResponse,
#   DELETE /members/{member_id} documents its no-content success response,
#   and GET /members/{member_id}/books returns an array of BookResponse.
#
# test_openapi_documents_success_and_error_statuses_for_each_operation
#   Assert the operation's success status (200, 201, or 204) and relevant
#   documented 401/403, 404, 409, and 422 statuses. Keep expectations tied to
#   the operation: for example, book creation documents a missing-member 404
#   and duplicate-ISBN 409; member deletion documents missing-member 404 and
#   member-has-books 409.
#
# test_openapi_request_schemas_declare_the_expected_required_fields
#   Resolve component references and check BookCreate/BookUpdate and
#   MemberCreate/MemberUpdate properties and required fields against the
#   application schemas.
#
# test_openapi_validation_errors_publish_http_validation_error_schema
#   Check typed path parameters and request bodies document 422 responses with
#   the standard HTTPValidationError response schema.
#
# test_openapi_domain_error_schemas_match_http_error_bodies
#   Check the documented 404 and 409 response content/schema agrees with the
#   actual {"detail": "..."} error body used by the routers.
#
# Contract gap to address when implementing: current explicit 404/409 route
# responses generally provide descriptions but no response content/schema.
# Add the response schemas to the API documentation before asserting that their
# body shapes are published; do not treat a description-only response as
# documenting the error body.
