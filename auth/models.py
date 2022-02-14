import datetime
from core.db import Base
from sqlalchemy import Column, String, Integer, DateTime, Interval


class Application(Base):

    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    app_name = Column(String(length=200), nullable=False, unique=True)
    app_id = Column(String(length=40), nullable=False, unique=True)
    app_secret = Column(String(length=128), nullable=False)
    date_of_add = Column('date_of_add', DateTime, default=datetime.datetime.now, nullable=False)
    date_of_update = Column('date_of_update', DateTime, default=datetime.datetime.now,
                            onupdate=datetime.datetime.now, nullable=False)
