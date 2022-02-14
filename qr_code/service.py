from sqlalchemy.sql.elements import or_
from core.utils import get_db

from core.db import Base
from pydantic import BaseModel
from fastapi import Query, Depends, Request, HTTPException, status
from typing import Optional
from sqlalchemy.orm import Session
import sys
import math


def str_to_class(classname):
    return getattr(sys.modules[__name__], classname)


def ordering_parameters(ordering: Optional[str] = Query("id")):
    return {"ordering": ordering}


def pagination_parameters(page: Optional[int] = Query(1, ge=1),
                          page_size: Optional[int] = Query(10, ge=1, le=1000)):
    return {"page": page, "page_size": page_size}


def search_parameters(search: Optional[str] = Query(None, max_length=100)):
    return {'search': search}


def default_parameters(request: Request, db: Session = Depends(get_db), ):
    return {'request': request, 'db': db}


def default_list_parameters(default_params: dict = Depends(default_parameters),
                            ordering: dict = Depends(ordering_parameters),
                            page: dict = Depends(pagination_parameters),
                            search: dict = Depends(search_parameters)):

    return {'default_params': default_params, "ordering": ordering, "page": page, "search": search}


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
        for parameter in ['params', 'model', 'search_fields']:
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

    def order(self, query):
        return query.order_by(
                getattr(getattr(self.model, self.ordering['value']), self.ordering['type'])())


class SearchMixin(MixinBase):
    def search_objects(self, query):

        parameters = [getattr(self.model, f"{field}").ilike('%' + str(self.search) + '%') for
                      field in self.search_fields if getattr(self.model, f"{field}").type.python_type == str]

        return query.filter(or_(*parameters))


class ListMixin(OrderMixin, SearchMixin, FilterMixin, PaginatorMixin):
    model = None
    params = None

    def __init__(self, params: dict,):
        super().__init__()
        self.params = params
        self.db = params['params']['default_params']['db']
        self.model = params['model']
        self.page = params['params']['page']['page']
        self.page_size = params['params']['page']['page_size']
        self.ordering = params['params']['ordering']
        self.search = params['params']['search']['search']
        self.search_fields = params['search_fields']
        self.clear_params()
        self.set_meta_attributes()

    def get_list(self):

        if self.params_is_null():
            query = self.db.query(self.model)
        else:
            query = self.filter_list()

        if self.search:
            query = self.search_objects(query)

        query = self.order(query)

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

    def get_or_404(self):
        obj = self.get_detail()
        if not obj:
            raise HTTPException(detail="Not found", status_code=status.HTTP_404_NOT_FOUND)
        return obj


class CreateMixin:
    def __init__(self, db: Session, model: Base,):
        self.db = db
        self.model = model

    def create_object(self, item):
        obj = self.model(**item.dict())
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def check_uniq(self, attribute: str, value: str):
        q = self.db.query(self.model).filter(getattr(self.model, attribute) == value)
        return self.db.query(q.exists()).scalar()


class UpdateMixin:
    def __init__(self, db: Session, model: Base,):
        self.db = db
        self.model = model

    def update(self, db_object: BaseModel, new_object: BaseModel):

        for attribute, value in vars(new_object).items():
            setattr(db_object, attribute, value) if value else None

        self.db.add(db_object)
        self.db.commit()
        self.db.refresh(db_object)

        return db_object
