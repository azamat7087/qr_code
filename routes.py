from fastapi import APIRouter
from qr_code import qr_code

routes = APIRouter()

routes.include_router(qr_code.router, prefix="/qr_code")
