from pydantic import BaseModel, Field, field_validator, ConfigDict


class CreateCategoryInputDTO(BaseModel):
    """Input DTO for category creation"""

    name: str = Field(min_length=1, max_length=100, description="Category name")
    color: str | None = Field(
        default=None, max_length=7, description="Color hex code (e.g., #FF5733)"
    )
    icon: str | None = Field(default=None, max_length=50, description="Icon identifier")

    @field_validator("name")
    @classmethod
    def name_must_not_be_only_whitespace(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be only whitespace")
        return v.strip()

    @field_validator("color")
    @classmethod
    def color_must_be_valid_hex(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if not v.startswith("#") or len(v) != 7:
            raise ValueError("Color must be in hex format #RRGGBB")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"name": "Electronics", "color": "#FF5733", "icon": "laptop"}
        }
    )
