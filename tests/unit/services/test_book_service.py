# Planned unit tests for both Book service implementations.
#
# InMemoryBookService
# -------------------
# test_in_memory_book_service_creates_and_retrieves_a_book
#   Seed a member, create a book, then retrieve/list it and check its assigned ID.
#
# test_in_memory_book_service_rejects_a_book_for_a_missing_member
#   Check that create and replace reject a member_id absent from the shared store.
#
# test_in_memory_book_service_reports_missing_books
#   Check get, replace, and delete behavior for an unknown book ID.
#
# test_in_memory_book_service_rejects_duplicate_normalized_isbns
#   Check duplicate detection when ISBNs differ only by case, spaces, or hyphens.
#
# test_in_memory_book_service_allows_a_book_to_keep_its_isbn_on_replace
#   Check replacement does not treat the book's own ISBN as a duplicate.
#
# test_in_memory_book_service_replaces_and_deletes_a_book
#   Check successful replacement and deletion are reflected in subsequent reads.
#
# DatabaseBookService without PostgreSQL
# ---------------------------------------
# test_database_book_service_creates_when_member_exists
#   Use a fake session factory and repository doubles; check member lookup,
#   duplicate lookup, repository create, and returned book behavior.
#
# test_database_book_service_rejects_missing_member_or_duplicate_isbn
#   Use repository doubles to drive each domain-error branch without a database.
#
# test_database_book_service_reports_missing_book
#   Use a repository double returning no book and check BookNotFoundError.
#
# test_database_book_service_rejects_missing_replacement_member
#   Use repository doubles to check replacement's member relationship decision.
#
# test_database_book_service_rejects_duplicate_isbn_from_another_book
#   Use repository doubles to distinguish another book's ISBN from the current
#   book's ISBN.
#
# test_database_book_service_deletes_an_existing_book
#   Use a repository double and fake transaction to check the delete decision.
#
# Keep these unit tests independent of PostgreSQL; real SQLAlchemy behavior
# belongs in tests/integration/test_repositories.py.
