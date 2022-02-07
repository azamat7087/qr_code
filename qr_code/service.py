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


def search_parameters(search: Optional[str] = Query(None, max_length=100)):
    return {'search': search}


class MixinBase:
    def __init__(self):
        self.params = None
        self.db = None
        self.model = None
        self.page = None
        self.page_size = None
        self.reverse = None
        self.query = None
        self.count = None
        self.count_of_pages = None
        self.ordering = None
        self.search = None
        self.search_fields = None


class PaginatorMixin(MixinBase):

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

            return self.query.limit(right).offset(left).all()

        except Exception as e:
            if str(e) == f"Page is too large. Max page {self.count_of_pages}":
                return []
            elif str(e) == "There is only 1 page":
                return self.query.all()

    def paginate(self, query):
        self.query = query
        self.count = len(query.all())
        self.count_of_pages = math.ceil(self.count / self.page_size)

        page = self.get_page()
        count = self.count
        count_of_pages = self.count_of_pages
        return {"results": page, "count": count, "count_of_pages": count_of_pages}


class FilterMixin(MixinBase):

    def clear_params(self):
        for parameter in ['request', 'db', 'ordering', 'page', 'search', 'model', 'search_fields']:
            self.params.pop(parameter)

    def params_is_null(self):
        return all(not value for value in self.params.values())

    def filter_list(self):
        return self.db.query(self.model).filter_by(**self.params)


class OrderMixin(MixinBase):
    def set_meta_attributes(self):

        if "-" in self.ordering['ordering']:
            self.ordering = {'value': self.ordering['ordering'].replace("-", ""), 'type': 'desc'}
        else:
            self.ordering = {'value': self.ordering['ordering'], 'type': 'asc'}


class SearchMixin(MixinBase):
    def search_objects(self, query):
        return query.filter(self.model.url.like('%' + str(self.search) + '%'))  # поиск по нескольким параметрам


class ListMixin(OrderMixin, SearchMixin, FilterMixin, PaginatorMixin):

    def __init__(self, params: dict,):
        super().__init__()
        self.params = params
        self.db = params['db']
        self.model = params['model']
        self.page = params['page']['page']
        self.page_size = params['page']['page_size']
        self.ordering = params['ordering']
        self.search = params['search']['search']
        self.search_fields = params['search_fields']
        self.clear_params()
        self.set_meta_attributes()

    def get_list(self):
        """

        Замутить поиск и провести рефакторинг. Возможно повысить уровень абстракции

        """

        if self.params_is_null():
            query = self.db.query(self.model)
        else:
            query = self.filter_list()

        if self.search:
            query = self.search_objects(query)

        query = query.order_by(
                getattr(getattr(self.model, self.ordering['value']), self.ordering['type'])())

        if query:
            paginated = self.paginate(query)

            return {"count": paginated["count"],
                    "page": f"{self.page} / {paginated['count_of_pages']}",
                    "results": paginated["results"]}

        return None


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
