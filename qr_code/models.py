import datetime

from core.db import Base
from sqlalchemy import Column, String, Integer, DateTime


class QRCode(Base):
    __tablename__ = "qr_codes"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    url = Column(String(length=300), nullable=False, unique=True)
    qr_code = Column(String(length=300), nullable=False)
    source_ip = Column(String(length=16))
    date_of_add = Column('date_of_add', DateTime, default=datetime.datetime.now(), nullable=False)
    date_of_update = Column('date_of_update', DateTime, default=datetime.datetime.now(),
                            onupdate=datetime.datetime.now(), nullable=False)

