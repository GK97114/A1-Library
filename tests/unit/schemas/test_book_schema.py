# Planned unit tests for the application-defined Book Pydantic schemas.
#
# test_book_create_requires_each_application_field
#   Check that omitting title, author, isbn, published_year, or member_id is rejected.
#   Keep id out of BookCreate's required-field checks; it is supplied by persistence.
#
# test_book_response_requires_a_positive_id
#   Check that BookResponse requires id and rejects zero or negative IDs.
#
# test_book_create_accepts_text_length_boundaries
#   Check minimum and maximum title (1/200), author (1/120), and ISBN (10/17)
#   lengths; check published_year at 1450 and the schema's current_year.
#
# test_book_create_rejects_text_lengths_outside_boundaries
#   Check title, author, and ISBN below/above their declared lengths.
#
# test_book_create_rejects_invalid_published_year
#   Check a year below 1450 and a year later than current_year.
#
# test_book_create_rejects_nonpositive_member_id
#   Check member_id values of zero and below.
#
# test_book_create_trims_surrounding_whitespace
#   Check that configured string fields are stored without leading/trailing spaces.
#
# test_book_create_rejects_whitespace_only_required_text
#   Check that trimming does not allow title, author, or ISBN to become empty.
#
# test_book_create_rejects_unknown_fields
#   Check that extra="forbid" rejects an unrecognized input key.
#
# test_book_update_applies_the_same_book_field_rules
#   Check that replacement input uses the shared BookBase validation rules.
#
# Note: ISBN currently has length rules only; these tests should not assume an
# ISBN checksum or character-format rule that the schema does not declare.
