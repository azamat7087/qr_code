from core.db import Base
from pydantic import BaseModel
from fastapi import Query
from typing import Optional
from sqlalchemy.orm import Session
import sqlalchemy
import sys


def str_to_class(classname):
    return getattr(sys.modules[__name__], classname)


def ordering_parameters(ordering: Optional[str] = Query("id")):
    return {"ordering": ordering}


class ListMixin:

    def __init__(self, db: Session, model: Base, params: dict, ordering: dict):
        self.params = params
        self.db = db
        self.model = model

        self.params.pop('request')
        self.params.pop('db')
        self.params.pop('ordering')

        self.reverse = {'asc': False, 'desc': True}

        if "-" in ordering['ordering']:
            self.ordering = {'value': ordering['ordering'].replace("-", ""), 'type': 'desc'}
        else:
            self.ordering = {'value': ordering['ordering'], 'type': 'asc'}

    def is_null(self):
        return all(not value for value in self.params.values())

    def order_list(self, query):
        return sorted(query, key=lambda x: getattr(x, self.ordering['value']), reverse=self.reverse[self.ordering['type']])

    def filter_list(self):
        filter_set = list()

        for attr in [x for x in self.params if self.params[x] is not None]:
            filter_set.append(set(self.db.query(self.model).filter(getattr(self.model, attr) == self.params[attr]).all()))
        query = self.order_list(set.intersection(*filter_set))

        if not query:
            query = None

        return query

    def get_list(self):
        """

        Проверить скорость работы через списки и через ordering

        Пагинация и поиск

        """
        query = self.db.query(self.model).order_by(getattr(getattr(self.model, self.ordering['value']), self.ordering['type'])()).all()

        if not self.is_null():
            query = self.filter_list()

        return query


class DetailMixin:
    def __init__(self, query_value: list, db: Session, model: Base):
        self.query_value = query_value
        self.db = db
        self.model = model

    def get_detail(self):
        return self.db.query(self.model).filter(getattr(self.model, self.query_value[0]) == self.query_value[1]).scalar()


class CreateMixin:
    def __init__(self, db: Session, item: BaseModel, model: Base,):
        self.db = db
        self.item = item
        self.model = model

    def create_object(self):
        obj = self.model(**self.item.dict())
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def check_uniq(self, attribute: str, value: str):
        q = self.db.query(self.model).filter(getattr(self.model, attribute) == value)
        return self.db.query(q.exists()).scalar()
