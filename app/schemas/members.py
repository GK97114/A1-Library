from pydantic import BaseModel, ConfigDict, EmailStr, Field

class MemberBase(BaseModel):
    """Define fields shared by all Member schemas"""
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    name: str = Field(
        required=True,
        min_length=1,
        max_length=120
    )

    email: EmailStr = Field(
        required=True,
    )

    memberships_id: str = Field(
        required=True,
    )

    phone: str = Field(
        required=True,
        pattern=r"^\(\d{3}\)-\d{3}-\d{4}$", #US. phone number format (###)-###-####
    )

class MemberCreate(MemberBase):
    """Validate the body used to create a new member"""

class MemberUpdate(MemberBase):
    """Validate the replacement body used to update an existing member"""

class MemberResponse(MemberBase):
    """Describe a member returned by the API."""

    id: int = Field(
        gt=0,
        description="The unique identifier for the member",
        examples=[1],   # Provide an example of a valid member ID
    )