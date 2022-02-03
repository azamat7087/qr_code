from fastapi import Body, HTTPException, APIRouter, Request
from qr_code.schemas import Url
from .utils import parse_url, generate_image
from core.s3 import client, BUCKET
import os

router = APIRouter()


@router.post("/generate")
async def generate(request: Request, url: Url = Body(...),):
    path = os.getcwd()
    client_host = request.client.host
    print(client_host)
    try:
        url = url.url

        name = await parse_url(url)
        file_name = f'{path}/temp/{name}.png'

        await generate_image(url, file_name)

        client.upload_file(f"{file_name}", BUCKET, f"qr_code/{name}.png")

        response = client.generate_presigned_url('get_object',
                                                 Params={'Bucket': BUCKET,
                                                         'Key': f"qr_code/{name}.png"},
                                                 ExpiresIn=300)

        os.remove(file_name)

        return {"image": response}
    except OSError as e:
        return HTTPException(status_code=400, detail=f"Something wrong: {str(e)}")