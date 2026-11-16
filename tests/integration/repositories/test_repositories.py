# Planned integration tests for repositories using real SQLAlchemy mappings
# and a disposable PostgreSQL database from tests/integration/conftest.py.
#
# test_member_repository_persists_and_finds_members
#   Check create, generated positive ID, get-by-ID, get-by-email,
#   get-by-membership-ID, and ordered list behavior.
#
# test_book_repository_persists_and_finds_books
#   Check create, generated positive ID, get-by-ID, get-by-ISBN, and ordered
#   list behavior using real Book/Member mappings.
#
# test_book_repository_lists_books_for_their_member
#   Check member filtering and ID ordering for list_by_member/exists_for_member.
#
# test_postgres_rejects_duplicate_member_email
#   Check the real unique constraint rejects a second Member with the same email.
#
# test_postgres_rejects_duplicate_membership_id
#   Check the real unique constraint rejects a second Member with the same
#   membership_id.
#
# test_postgres_rejects_duplicate_book_isbn
#   Check the real unique constraint rejects a second Book with the same ISBN.
#
# test_postgres_rejects_book_with_missing_member
#   Check the Member-to-Book foreign key rejects a book referencing no member.
#
# test_postgres_allows_book_with_existing_member
#   Check a persisted Book references its existing Member through member_id.
#
# These tests must use the temporary container fixture, not a local PostgreSQL
# server or the developer's Library database.
