from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timedelta


class ApplicationBase(BaseModel):
    app_id: str

    class Config:
        orm_mode = True


class Application(ApplicationBase):
    app_secret: str

    class Config:
        orm_mode = True


class ApplicationDB(Application):
    id: int
    date_of_add: datetime = Field(None)
    date_of_update: datetime = Field(None)

    class Config:
        orm_mode = True

        the_schema = {
            "id": 1,
            "app_id": "test",
            "app_secret": "test",
            "date_of_add": datetime.now(),
            "date_of_update": datetime.now()
        }
