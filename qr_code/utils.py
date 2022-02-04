import qrcode
import random
import os
from time import time


async def parse_url(url: str):
    try:
        return url.split("/")[2].replace(".", "_") + str(time()).split(".")[0]
    except Exception as e:
        return str(time()).split(".")[0]


async def generate_image(url, name):
    path = os.getcwd()
    file_name = f'{path}/temp/{name}.png'
    qrcode_image = qrcode.make(f"{url}")
    qrcode_image.save(f'{file_name}', 'PNG')
    return file_name


async def upload_s3(client, file_name, bucket, name):
    client.upload_file(f"{file_name}", bucket, f"qr_code/{name}.png")

    link = client.generate_presigned_url('get_object',
                                         Params={'Bucket': bucket,
                                                 'Key': f"qr_code/{name}.png"},
                                         ExpiresIn=1300)
    return link


async def get_meta_data(url, request, client, bucket):

    name = await parse_url(url)
    file_name = await generate_image(url, name)
    source_ip = request.client.host
    link = await upload_s3(client=client, file_name=file_name, bucket=bucket, name=name)

    return {"name": name, "file_name": file_name, "source_ip": source_ip, "link": link}
