# Planned unit tests for both Member service implementations.
#
# InMemoryMemberService
# ---------------------
# test_in_memory_member_service_creates_and_retrieves_a_member
#   Check successful create, assigned ID, get, and list behavior.
#
# test_in_memory_member_service_reports_a_missing_member
#   Check get, replace, delete, and list-books behavior for an unknown ID.
#
# test_in_memory_member_service_lists_only_the_members_books
#   Seed multiple members and books; check the relationship filter.
#
# test_in_memory_member_service_blocks_deletion_when_books_exist
#   Check MemberHasBooksError and verify the member remains in the store.
#
# test_in_memory_member_service_deletes_a_member_without_books
#   Check successful deletion when no book references the member.
#
# test_in_memory_member_service_rejects_duplicate_email_or_membership_id
#   Check each duplicate rule, including the implementation's case-insensitive
#   comparisons.
#
# DatabaseMemberService without PostgreSQL
# -----------------------------------------
# test_database_member_service_creates_when_identifiers_are_unique
#   Use a fake session factory and repository doubles to check the unique checks
#   and create decision.
#
# test_database_member_service_rejects_duplicate_email_or_membership_id
#   Use repository doubles to drive each duplicate branch without a database.
#
# test_database_member_service_reports_a_missing_member
#   Use repository doubles returning no member for get, replace, or delete.
#
# test_database_member_service_lists_only_the_members_books
#   Use repository doubles to check the member-exists guard and book query.
#
# test_database_member_service_blocks_deletion_when_books_exist
#   Use repository doubles to report an existing relationship and check that
#   the member repository's delete operation is not called.
#
# test_database_member_service_deletes_a_member_without_books
#   Use repository doubles to check the no-books delete path.
#
# Fake sessions/repositories here only isolate service decisions. Validate real
# mappings, transactions, and constraints in the integration repository tests.
