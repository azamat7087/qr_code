from core.db import Base
from sqlalchemy import Column, String, Integer, Text, DateTime


class QRCode(Base):
    __tablename__ = "qr_codes"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    url = Column(String(length=300), )
    qr_code = Column(Text, )
    user_ip = Column(String(length=16))
    date = Column(DateTime)
