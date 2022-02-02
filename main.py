from fastapi import FastAPI, Body, HTTPException
from schemas import Url
import uvicorn
import qrcode
import random
import boto3
import os

app = FastAPI()

path = os.getcwd()

ACCESS_KEY = os.environ.get('S3_ACCESS_KEY', "fNhUxNGK2FGafTqy")
SECRET_KEY = os.environ.get('S3_SECRET_KEY', "MjhYNvJ72VaAG9fmjYDuAhg8T7vW6d3v")

client = boto3.client("s3",
                      endpoint_url="https://s3.azat.ai",
                      aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY
                      )
BUCKET = "public"


async def parse_url(url: str):
    try:
        if "www" in url:
            return url.split("//")[1].split("/")[1].split(".")[0] + str(random.randint(0, 100))
        else:
            return url.split("//")[1].split("/")[0].split(".")[0] + str(random.randint(0, 100))

    except Exception:
        return str(random.randint(0, 100))


async def generate_image(url, file_name):
    qrcode_image = qrcode.make(f"{url}")
    qrcode_image.save(f'{file_name}', 'PNG')


@app.post("/generate")
async def generate(url: Url = Body(..., )):

    try:
        url = url.url

        name = await parse_url(url)
        file_name = f'{path}/{name}.png'

        await generate_image(url, file_name)

        client.upload_file(f"{name}.png", BUCKET, f"qr_code/{name}.png")

        response = client.generate_presigned_url('get_object',
                                                 Params={'Bucket': BUCKET,
                                                         'Key': f"qr_code/{name}.png"},
                                                 ExpiresIn=300)

        os.remove(file_name)

        return {"image": response}
    except OSError as e:
        return HTTPException(status_code=400, detail=f"Something wrong: {str(e)}")

