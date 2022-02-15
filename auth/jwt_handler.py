import time
from datetime import datetime, timedelta
import jwt
import os

from fastapi import HTTPException

SECRET = os.environ.get('FASTAPI_SECRET', '02d8d1c5af26263eb6346f7bd288997d4bd47d95')
ALGORITHM = os.environ.get('FASTAPI_ALGORITHM', "HS256")


def token_response(token: str):
    return {
        "access_token": token
    }


def signJWT(app_id: str):
    payload = {
        "app_id": app_id,
        "expiry": time.time() + 1800  # 30 min
    }

    token = jwt.encode(payload, SECRET, algorithm=ALGORITHM)

    return token_response(token)


def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        return decoded_token if decoded_token["expiry"] >= time.time() else None
    except:
        return {}
