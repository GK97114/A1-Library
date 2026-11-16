# Planned unit tests for the application-defined Member Pydantic schemas.
#
# test_member_create_requires_each_application_field
#   Check that omitting name, email, membership_id, or phone is rejected.
#   Keep id out of MemberCreate's required-field checks; persistence supplies it.
#
# test_member_response_requires_a_positive_id
#   Check that MemberResponse requires id and rejects zero or negative IDs.
#
# test_member_create_accepts_name_and_membership_id_length_boundaries
#   Check name lengths 1/120 and membership_id's declared maximum length of 20.
#
# test_member_create_rejects_name_and_membership_id_overlength_values
#   Check name over 120 and membership_id over 20 characters.
#
# test_member_create_accepts_a_valid_email_at_the_length_limit
#   Check a syntactically valid email no longer than 100 characters.
#
# test_member_create_rejects_malformed_and_overlength_emails
#   Check invalid email syntax and an email longer than 100 characters.
#
# test_member_create_accepts_the_declared_phone_format
#   Check a phone value matching (###)-###-####.
#
# test_member_create_rejects_phone_values_outside_the_declared_format
#   Check missing punctuation, wrong digit counts, and non-digit characters.
#
# test_member_create_trims_surrounding_whitespace
#   Check whitespace trimming for the string fields, including name and phone.
#
# test_member_create_rejects_unknown_fields
#   Check that extra="forbid" rejects an unrecognized input key.
#
# test_member_update_applies_the_same_member_field_rules
#   Check that replacement input uses the shared MemberBase validation rules.
#
# Note: membership_id currently has no minimum length, and phone has a format
# pattern but no length setting. Decide whether empty membership IDs should be
# accepted before writing an expectation beyond the rules currently declared.
