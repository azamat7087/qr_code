from fastapi import Body, HTTPException, APIRouter, Request, Depends, Path, Query, status
from qr_code.schemas import QRCodeCreate, QRCodeDetail, QRCodeFull, PaginatedSchema
from qr_code.models import QRCode
from .utils import get_meta_data
from core.utils import get_db
from core.s3 import client, BUCKET
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Union
import qr_code.service as service
import os

router = APIRouter()


@router.post("/", response_model=QRCodeDetail, status_code=status.HTTP_201_CREATED, tags=['QR code'])
async def qrcode_generate(request: Request,
                          qr_code: QRCodeCreate = Body(...,),
                          db: Session = Depends(get_db)):

    try:
        url = qr_code.url

        if service.CreateMixin(db=db, item=qr_code, model=QRCode).check_uniq(attribute='url', value=url):
            return service.DetailMixin(query_value=["url", url], db=db, model=QRCode).get_detail()

        data = await get_meta_data(url=url, request=request, client=client, bucket=BUCKET)

        qr_code = QRCodeFull(**qr_code.dict(),
                             source_ip=data['source_ip'],
                             qr_code=data['link']
                             )

        qr_code = service.CreateMixin(db, qr_code, QRCode).create_object()

        os.remove(data['file_name'])

        return qr_code
    except OSError as e:
        return HTTPException(status_code=400, detail=f"Something wrong: {str(e)}")


@router.get("/", response_model=PaginatedSchema, tags=['QR code'])
async def qrcode_list(request: Request,
                      db: Session = Depends(get_db),
                      source_ip: Optional[str] = Query(None, max_length=17,),
                      ordering: dict = Depends(service.ordering_parameters),
                      page: dict = Depends(service.pagination_parameters),
                      search: dict = Depends(service.search_parameters)):

    params = locals().copy()
    params['model'] = QRCode
    params['search_fields'] = ['qr_code', 'url', 'id']
    qr_codes = service.ListMixin(params=params).get_list()

    return qr_codes


@router.get("/{pk}", response_model=QRCodeDetail, tags=['QR code'])
async def qrcode_detail(request: Request,
                        pk: int = Path(..., description="The ID of the qr code object", gt=0),
                        db: Session = Depends(get_db)):

    qr_code = service.DetailMixin(query_value=["id", pk], db=db, model=QRCode).get_detail()
    return qr_code
