from core.db import Base
from pydantic import BaseModel
from fastapi import Query
from typing import Optional
from sqlalchemy.orm import Session
import sys
import math


def str_to_class(classname):
    return getattr(sys.modules[__name__], classname)


def ordering_parameters(ordering: Optional[str] = Query("id")):
    return {"ordering": ordering}


def pagination_parameters(page: Optional[int] = Query(1, ge=1),
                          page_size: Optional[int] = Query(10, ge=1)):
    return {"page": page, "page_size": page_size}


class Paginator:
    def __init__(self, query: list, page: int, page_size: int):
        self.query = query.copy()
        self.count = len(query)
        self.page_size = page_size
        self.page = page
        self.count_of_pages = math.ceil(self.count / self.page_size)

    def validate(self):
        if self.page > self.count_of_pages:
            raise Exception(f"Page is too large. Max page {self.count_of_pages}")

        if self.count_of_pages == 1:
            raise Exception("There is only 1 page")

    def get_page(self):
        try:
            self.validate()
            if not self.page == self.count_of_pages:
                right = self.page * self.page_size
                left = right - self.page_size
            else:
                right = self.count
                left = (self.page - 1) * self.page_size
            return self.query[left:right]

        except Exception as e:
            if str(e) == f"Page is too large. Max page {self.count_of_pages}":
                return []
            elif str(e) == "There is only 1 page":
                return self.query


class ListMixin:

    def __init__(self, db: Session, model: Base, params: dict, ordering: dict, page: dict):

        self.params = params
        self.db = db
        self.model = model
        self.page = page['page']
        self.page_size = page['page_size']

        self.clear_params()

        self.reverse = {'asc': False, 'desc': True}

        if "-" in ordering['ordering']:
            self.ordering = {'value': ordering['ordering'].replace("-", ""), 'type': 'desc'}
        else:
            self.ordering = {'value': ordering['ordering'], 'type': 'asc'}

    def clear_params(self):
        for parameter in ['request', 'db', 'ordering', 'page']:
            self.params.pop(parameter)

    def is_null(self):
        return all(not value for value in self.params.values())

    def sort_list(self, query):
        return sorted(query, key=lambda x: getattr(x, self.ordering['value']), reverse=self.reverse[self.ordering['type']])

    def paginate(self, query):
        paginator = Paginator(query=query, page=self.page, page_size=self.page_size)
        page = paginator.get_page()
        count = paginator.count
        count_of_pages = paginator.count_of_pages
        return page, count, count_of_pages

    def filter_list(self):
        filter_set = list()

        for attr in [x for x in self.params if self.params[x] is not None]:
            filter_set.append(set(self.db.query(self.model).filter(getattr(self.model, attr) == self.params[attr]).all()))
        query = self.sort_list(set.intersection(*filter_set))

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

        if query:
            paginated = self.paginate(query)
            return {"count": paginated[1], "page": f"{self.page}/{paginated[2]}", "results": paginated[0]}

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
