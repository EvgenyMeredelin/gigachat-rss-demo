from datetime import datetime
from typing import Annotated

from pydantic import (
    BaseModel, ConfigDict, Field, field_validator,
    AwareDatetime, NonNegativeFloat, PositiveFloat, PositiveInt
)


class ExpandableBaseModel(BaseModel):
    """A `BaseModel` clone that allows extra fields. """

    model_config = ConfigDict(extra="allow")


class GigaChatSettings(ExpandableBaseModel):
    """Selected settings to initialize GigaChat. """

    temperature: Annotated[
        PositiveFloat | None,
        Field(description="Valid range: (0, +inf).")
    ] = None
    top_p: Annotated[
        NonNegativeFloat | None,
        Field(le=1.0, description="Valid range: [0, 1].")
    ] = None
    max_tokens: PositiveInt | None = None
    profanity_check: bool | None = None
    timeout: PositiveInt | None = None


class GigaChatAccessToken(BaseModel):
    """A temporary access token to the GigaChat API. """

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    value: Annotated[str, Field(alias="token")]
    minutes_valid: PositiveInt
    released: AwareDatetime
    expires: AwareDatetime
    obs_key: str | None = None

    @field_validator("released", "expires", mode="before")
    @classmethod
    def convert_isoformat_to_datetime(cls, value: str) -> AwareDatetime:
        return datetime.fromisoformat(value)
