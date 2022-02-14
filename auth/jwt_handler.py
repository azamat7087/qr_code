import datetime
import time
import jwt
import os

SECRET = os.environ.get('FASTAPI_SECRET', '02d8d1c5af26263eb6346f7bd288997d4bd47d95')
ALGORITHM = os.environ.get('FASTAPI_ALGORITHM', "HS256")


def token_response(token: str):
    return {
        "access_token": token
    }


def signJWT(app_id: str):
    payload = {
        "app_id": app_id,
        "expiry": time.time() + 600
    }

    token = jwt.encode(payload, SECRET, algorithm=ALGORITHM)

    return token_response(token)


def decodeJWT(token: str):
    try:
        decode_token = jwt.decode(token, key=SECRET, algorithms=ALGORITHM)
        return decode_token if decode_token['expires'] >= time.time() else None
    except Exception as e:
        raise Exception(str(e))
