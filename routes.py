from fastapi import APIRouter
from qr_code import qr_code
from auth import auth

routes = APIRouter()

routes.include_router(qr_code.router, prefix="/qr_code")
routes.include_router(auth.router, prefix="/auth")
