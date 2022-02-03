import qrcode
import random
import os


async def parse_url(url: str):
    try:
        if "www" in url:
            return url.split("//")[1].split("/")[0].split(".")[1] + str(random.randint(0, 100))
        else:
            return url.split("//")[1].split("/")[0].split(".")[0] + str(random.randint(0, 100))
    except Exception as e:
        return str(random.randint(0, 100))


async def generate_image(url, file_name):
    qrcode_image = qrcode.make(f"{url}")
    qrcode_image.save(f'{file_name}', 'PNG')
