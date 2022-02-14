from pydantic import BaseModel, Field
from typing import Optional
from auth.models import Application
from datetime import datetime, timedelta


class ApplicationCreate(BaseModel):
    app_name: str = Field(..., max_length=200)

    class Config:
        orm_mode = True
        orm_model = Application


class ApplicationLogin(BaseModel):
    app_id: str = Field(..., max_length=41, )
    app_secret: str = Field(..., max_length=129,)

    class Config:
        orm_mode = True
        orm_model = Application


class ApplicationBase(ApplicationCreate, ApplicationLogin):

    class Config:
        orm_mode = True
        orm_model = Application


class ApplicationDB(Application):
    id: int
    date_of_add: datetime = Field(None)
    date_of_update: datetime = Field(None)

    class Config:
        orm_mode = True
        orm_model = Application

        the_schema = {
            "id": 1,
            "app_name": "test",
            "app_id": "test",
            "app_secret": "test",
            "date_of_add": datetime.now(),
            "date_of_update": datetime.now()
        }
