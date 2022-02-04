from .models import QRCode
from core.db import Base
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .schemas import QRCodeCreate, QRCodeList
import sys


def str_to_class(classname):
    return getattr(sys.modules[__name__], classname)


def get_list(db: Session, model: Base):
    return db.query(model).all()


def get_detail(query_value: list, db: Session, model: Base):
    return db.query(model).filter(getattr(model, query_value[0]) == query_value[1]).scalar()


def create_object(db: Session, item: BaseModel, classname: str):
    obj = str_to_class(classname=classname)(**item.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def check_uniq(db: Session, model: Base, attribute: str, value: str):
    q = db.query(model).filter(getattr(model, attribute) == value)
    return db.query(q.exists()).scalar()
