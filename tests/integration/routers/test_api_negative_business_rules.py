# Planned HTTP negative tests for API business-rule failures and data integrity.
#
# Use a fresh backend client per test and provide a valid admin_headers token
# for protected writes. Verify error status and JSON detail shape. For each
# applicable case, exercise both memory_api_client and database_api_client so
# the API behavior agrees across service implementations.
#
# test_api_returns_documented_404_for_missing_book
#   Request a nonexistent Book by ID and assert HTTP 404 with the expected
#   detail body; then check the Books list was not changed.
#
# test_api_returns_documented_404_for_missing_member
#   Request a nonexistent Member by ID and assert HTTP 404 with the expected
#   detail body; then check the Members list was not changed.
#
# test_api_rejects_book_for_nonexistent_member_without_storing_it
#   POST a valid Book payload whose member_id does not exist; assert HTTP 404,
#   check the response body, and verify no Book was added.
#
# test_api_rejects_duplicate_isbn_without_changing_books
#   Create a Book, attempt another create with the same ISBN, assert HTTP 409
#   and the documented error body, then verify the original remains unchanged
#   and the list contains no extra record.
#
# test_api_rejects_duplicate_member_email_without_changing_members
#   Create a Member, attempt a second create with the same email, assert HTTP
#   409 and the documented error body, then verify the original and collection
#   remain unchanged.
#
# test_api_rejects_duplicate_membership_id_without_changing_members
#   Create a Member, attempt a second create with the same membership_id,
#   assert HTTP 409 and the documented error body, then verify no second
#   Member was stored.
#
# test_api_rejects_member_deletion_while_books_are_linked
#   Create a Member and a related Book, attempt to delete the Member, assert
#   HTTP 409 and the documented error body, then retrieve the Member and its
#   Book to prove the failed deletion did not corrupt the relationship.
#
# test_api_rejects_duplicate_values_on_replace_without_mutating_records
#   For Book ISBN and Member email/membership_id conflicts, attempt a PUT that
#   conflicts with a different existing record; assert HTTP 409 and verify the
#   original target and conflicting record both retain their prior values.
#
# Contract consistency requirement: each expected status and body must match
# the corresponding operation's OpenAPI response. Current explicit 404/409
# entries may only publish descriptions; add error-body schemas to OpenAPI
# before asserting the {"detail": "..."} shape is represented in the contract.
