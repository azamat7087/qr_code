import datetime

from fastapi import Body, HTTPException, APIRouter, Request, Depends, Path, Query, status
from qr_code.schemas import QRCodeCreate, QRCodeDetail, QRCodeFull, PaginatedSchema, QRCodeRegenerate
from qr_code.models import QRCode
from .utils import get_meta_data, get_s3_link
from core.utils import get_db
from core.s3 import client, BUCKET
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Union
import qr_code.service as service
import os

router = APIRouter()


async def check_expiration(expiration_date: datetime.datetime):
    if datetime.datetime.now() > expiration_date:
        raise HTTPException(status_code=400, detail="QR code created, but expired")


@router.post("/", response_model=QRCodeDetail, status_code=status.HTTP_201_CREATED, tags=['QR code'])
async def qrcode_generate(params: dict = Depends(service.default_parameters),
                          qr_code: QRCodeCreate = Body(...,)):

    try:
        create = service.CreateMixin(db=params['db'], model=QRCode)

        if create.check_uniq(attribute='url', value=qr_code.url):

            qr_code = service.DetailMixin(query_value=["url", qr_code.url], db=params['db'], model=QRCode).get_detail()

            await check_expiration(qr_code.expiration_date)

            return qr_code

        data = await get_meta_data(url=qr_code.url, request=params['request'],
                                   client=client, bucket=BUCKET, expiration=qr_code.expiration)

        qr_code = QRCodeFull(**qr_code.dict(),
                             file_name=data['name'],
                             source_ip=data['source_ip'],
                             qr_code=data['link'],
                             expiration_date=datetime.datetime.now() + qr_code.expiration
                             )

        qr_code = create.create_object(item=qr_code)

        os.remove(data['file_name'])

        return qr_code
    except OSError as e:
        return HTTPException(status_code=400, detail=f"Something wrong: {str(e)}")


@router.patch("/", response_model=QRCodeDetail, status_code=status.HTTP_205_RESET_CONTENT, tags=['QR code'])
async def qrcode_regenerate(params: dict = Depends(service.default_parameters),
                            qr_code: QRCodeCreate = Body(...,)):

    old_qr_code = service.DetailMixin(query_value=["url", qr_code.url], db=params['db'], model=QRCode).get_detail()

    if not old_qr_code:
        raise HTTPException(detail="QR code didn't created, please use POST request",
                            status_code=status.HTTP_400_BAD_REQUEST)

    new_link = await get_s3_link(client=client, bucket=BUCKET, name=old_qr_code.file_name, expiration=qr_code.expiration)

    qr_code = QRCodeRegenerate(**qr_code.dict(),
                               expiration_date=datetime.datetime.now() + qr_code.expiration,
                               qr_code=new_link)

    new_object = service.UpdateMixin(db=params['db'], model=QRCode).update(old_qr_code, qr_code)

    return new_object


@router.get("/", response_model=PaginatedSchema, tags=['QR code'])
async def qrcode_list(params: dict = Depends(service.default_list_parameters),
                      source_ip: Optional[str] = Query(None, max_length=17,),  # Фильтр
                      ):

    params = locals().copy()
    params['model'] = QRCode
    params['search_fields'] = ['qr_code', 'url']

    qr_codes = service.ListMixin(params=params).get_list()

    return qr_codes


@router.get("/{pk}", response_model=QRCodeDetail, tags=['QR code'])
async def qrcode_detail(params: dict = Depends(service.default_parameters),
                        pk: int = Path(..., description="The ID of the qr code object", gt=0),
                        ):

    qr_code = service.DetailMixin(query_value=["id", pk], db=params['db'], model=QRCode).get_detail()

    await check_expiration(qr_code.expiration_date)

    return qr_code
