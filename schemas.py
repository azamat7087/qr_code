from pydantic import BaseModel, Field, validator
import validators


class Url(BaseModel):
    url: str = Field(..., min_length=10, max_length=300)

    @validator('url')
    def validate_age(cls, value):
        if "http" not in value:
            raise ValueError('Use valid link')

        if not validators.url(value):
            raise ValueError('Use valid link')

        return value
