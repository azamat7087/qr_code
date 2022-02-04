from pydantic import BaseModel, Field, validator
from qr_code.models import QRCode
from datetime import datetime
import validators


class QRCodeBase(BaseModel):
    url: str = Field("https://azat.ai", min_length=10, max_length=300)


class QRCodeCreate(QRCodeBase):
    @validator('url')
    def validate_age(cls, value):
        if not validators.url(value):
            raise ValueError('Use valid link')

        return value


class QRCodeDetail(QRCodeBase):
    id: int
    qr_code: str

    class Config:
        orm_mode = True


class QRCodeList(QRCodeBase):
    id: int

    class Config:
        orm_mode = True


class QRCodeFull(QRCodeBase):
    id: int = Field(None)
    qr_code: str
    source_ip: str
    date_of_add: datetime = Field(None)
    date_of_update: datetime = Field(None)

    class Meta:
        orm_mode = True
        orm_model = QRCode
