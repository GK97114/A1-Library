"""Unit tests for the Member Pydantic schemas."""

import pytest
from pydantic import ValidationError

from app.models.members import Member
from app.schemas.members import MemberCreate, MemberResponse, MemberUpdate


def valid_member_data() -> dict[str, str]:
    """Return a valid Member payload that tests can modify independently."""
    return {
        "name": "Ada Lovelace",
        "email": "ada@example.com",
        "membership_id": "M-001",
        "phone": "(555)-123-4567",
    }


@pytest.mark.parametrize("field", ["name", "email", "membership_id", "phone"])
def test_member_create_requires_each_application_field(field: str) -> None:
    """Verify that each required field is indeed required."""
    payload = valid_member_data()
    del payload[field]

    with pytest.raises(ValidationError):
        MemberCreate.model_validate(payload)


def test_member_response_requires_a_positive_id() -> None:
    """Verify that the MemberResponse schema requires a positive ID."""
    payload = valid_member_data()

    with pytest.raises(ValidationError):
        MemberResponse.model_validate(payload)

    for member_id in (0, -1):
        with pytest.raises(ValidationError):
            MemberResponse.model_validate({**payload, "id": member_id})


def test_member_response_accepts_a_sqlalchemy_member() -> None:
    """Verify that the MemberResponse schema accepts a SQLAlchemy Member instance."""
    member = Member(id=1, **valid_member_data())

    response = MemberResponse.model_validate(member)

    assert response.id == 1
    assert response.email == "ada@example.com"


def test_member_create_accepts_name_and_membership_id_length_boundaries() -> None:
    """Verify that MemberCreate accepts valid name and membership ID lengths."""
    for name, membership_id in (("A", ""), ("N" * 120, "M" * 20)):
        member = MemberCreate.model_validate(
            {
                **valid_member_data(),
                "name": name,
                "membership_id": membership_id,
            }
        )
        assert member.name == name
        assert member.membership_id == membership_id


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("name", ""),
        ("name", "N" * 121),
        ("membership_id", "M" * 21),
    ],
)
def test_member_create_rejects_name_and_membership_id_outside_boundaries(
    field: str, value: str
) -> None:
    """Verify that MemberCreate rejects name and membership ID lengths outside the allowed boundaries."""
    with pytest.raises(ValidationError):
        MemberCreate.model_validate({**valid_member_data(), field: value})


def test_member_create_accepts_a_valid_email_at_the_length_limit() -> None:
    """Verify that MemberCreate accepts a valid email at the maximum allowed length."""
    email = f'{"a" * 64}@{"b" * 31}.com'
    assert len(email) == 100

    member = MemberCreate.model_validate({**valid_member_data(), "email": email})

    assert str(member.email) == email


@pytest.mark.parametrize(
    "email",
    [
        "not-an-email",
        f'{"a" * 64}@{"b" * 32}.com',
    ],
)
def test_member_create_rejects_malformed_and_overlength_emails(email: str) -> None:
    """Verify that MemberCreate rejects malformed and overlength emails."""
    with pytest.raises(ValidationError):
        MemberCreate.model_validate({**valid_member_data(), "email": email})


def test_member_create_accepts_the_declared_phone_format() -> None:
    """Verify that MemberCreate accepts the declared phone format."""
    member = MemberCreate.model_validate(
        {**valid_member_data(), "phone": "(123)-456-7890"}
    )
    assert member.phone == "(123)-456-7890"


@pytest.mark.parametrize(
    "phone",
    [
        "123-456-7890",
        "(12)-456-7890",
        "(123)-45-7890",
        "(123)-456-789",
        "(123)-456-789A",
    ],
)
def test_member_create_rejects_phone_values_outside_the_declared_format(
    phone: str,
) -> None:
    """Verify that MemberCreate rejects phone values outside the declared format."""
    with pytest.raises(ValidationError):
        MemberCreate.model_validate({**valid_member_data(), "phone": phone})


def test_member_create_trims_surrounding_whitespace() -> None:
    """Verify that MemberCreate trims surrounding whitespace from text fields."""
    member = MemberCreate.model_validate(
        {
            **valid_member_data(),
            "name": "  Ada Lovelace  ",
            "email": "  ada@example.com  ",
            "membership_id": " M-001 ",
            "phone": " (555)-123-4567 ",
        }
    )

    assert member.name == "Ada Lovelace"
    assert str(member.email) == "ada@example.com"
    assert member.membership_id == "M-001"
    assert member.phone == "(555)-123-4567"


def test_member_create_rejects_unknown_fields() -> None:
    """Verify that MemberCreate rejects unknown fields."""
    with pytest.raises(ValidationError):
        MemberCreate.model_validate({**valid_member_data(), "unknown": "value"})


def test_member_update_applies_the_same_member_field_rules() -> None:
    """Verify that MemberUpdate applies the same field validation rules as MemberCreate."""
    with pytest.raises(ValidationError):
        MemberUpdate.model_validate({**valid_member_data(), "phone": "5551234567"})

    updated = MemberUpdate.model_validate(
        {**valid_member_data(), "name": "  Updated name  "}
    )
    assert updated.name == "Updated name"
