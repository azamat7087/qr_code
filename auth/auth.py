from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter, Body, Depends, HTTPException, status
from auth.schemas import ApplicationCreate, ApplicationBase, ApplicationLogin
from auth.jwt_handler import signJWT
from auth.utils import get_data, check_app
from auth.models import Application
import core.service as service
import hashlib

router = APIRouter()


@router.post("/token/sign-in", tags=['Auth'])
async def application_sign_in(app: ApplicationLogin = Body(..., ), params: dict = Depends(service.default_parameters)):
    try:
        if check_app(app, params):
            return signJWT(app_id=app.app_id)
        else:
            raise Exception("Invalid credentials")
    except Exception as e:
        raise HTTPException(detail=f"Something wrong: {str(e)}", status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/token/sign-up", response_model=ApplicationBase, tags=['Auth'])
async def application_sign_up(app: ApplicationCreate = Body(..., ), params: dict = Depends(service.default_parameters)):
    try:
        create = service.CreateMixin(db=params['db'], model=Application)

        if create.check_uniq(attribute='app_name', value=app.app_name):
            raise Exception("This application is already exists")

        app_id, app_secret = await get_data()

        application = ApplicationBase(**app.dict(),
                                      app_id=app_id,
                                      app_secret=hashlib.sha256(str(app_secret).encode('utf-8')).hexdigest())

        application = create.create_object(item=application)

        application.app_secret = app_secret

        return application
    except Exception as e:
        raise HTTPException(detail=f"Something wrong: {str(e)}", status_code=status.HTTP_400_BAD_REQUEST)

