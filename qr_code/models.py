import datetime
from core.db import Base
from sqlalchemy import Column, String, Integer, DateTime, Interval


class QRCode(Base):

    '''

    Добавить дату истечения срока активности Exp(Timedelta), ExpDate(DateTime)
    Добавить API для обновления qr объекта
    '''

    __tablename__ = "qr_codes"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    url = Column(String(length=300), nullable=False, unique=True)
    file_name = Column(String(length=1000), default="example.png")
    qr_code = Column(String(length=300), nullable=False)
    source_ip = Column(String(length=40), nullable=False)
    expiration = Column(Interval, default=604800,)
    expiration_date = Column(DateTime,)
    date_of_add = Column('date_of_add', DateTime, default=datetime.datetime.now, nullable=False)
    date_of_update = Column('date_of_update', DateTime, default=datetime.datetime.now,
                            onupdate=datetime.datetime.now, nullable=False)
