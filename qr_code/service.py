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
    def __init__(self, page: int, page_size: int):
        self.page_size = page_size
        self.page = page

        self.query = None
        self.count = None
        self.count_of_pages = None

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

    def paginate(self, query):
        self.query = query
        self.count = len(query)
        self.count_of_pages = math.ceil(self.count / self.page_size)

        page = self.get_page()
        count = self.count
        count_of_pages = self.count_of_pages
        return {"results": page, "count": count, "count_of_pages": count_of_pages}


class Filter:

    def __init__(self, db: Session,  model: Base, params: dict):

        self.params = params
        self.db = db
        self.model = model
        self.clear_params()

    def clear_params(self):
        for parameter in ['request', 'db', 'ordering', 'page']:
            self.params.pop(parameter)

    def is_null(self):
        return all(not value for value in self.params.values())

    def filter_list(self):
        filter_set = list()

        for attr in [x for x in self.params if self.params[x] is not None]:
            filter_set.append(
                set(self.db.query(self.model).filter(getattr(self.model, attr) == self.params[attr]).all()))
        return set.intersection(*filter_set)


class Order:

    def __init__(self, ordering: dict,):

        self.reverse = {'asc': False, 'desc': True}

        if "-" in ordering['ordering']:
            self.ordering = {'value': ordering['ordering'].replace("-", ""), 'type': 'desc'}
        else:
            self.ordering = {'value': ordering['ordering'], 'type': 'asc'}

    def sort_list(self, query):
        return sorted(query, key=lambda x: getattr(x, self.ordering['value']),
                      reverse=self.reverse[self.ordering['type']])


class ListMixin:

    def __init__(self, db: Session, model: Base, params: dict, ordering: dict, page: dict):

        self.params = params
        self.db = db
        self.model = model
        self.page = page['page']
        self.page_size = page['page_size']

        self.filter = Filter(db=db, model=model, params=params)
        self.ordering = Order(ordering=ordering)
        self.paginator = Paginator(page=self.page, page_size=self.page_size)

    def get_list(self):
        """

        Замутить поиск и провести рефакторинг. Возможно повысить уровень абстракции

        """

        if not self.filter.is_null():
            query = self.filter.filter_list()
        else:
            query = self.db.query(self.model).order_by(
                getattr(getattr(self.model, self.ordering.ordering['value']), self.ordering.ordering['type'])()).all()

        if query:
            paginated = self.paginator.paginate(query)
            return {"count": paginated["count"],
                    "page": f"{self.page} / {paginated['count_of_pages']}",
                    "results": paginated["results"]}

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
