import requests
import json
import time
import math


def db_check():
    url = 'http://127.0.0.1:8000/qr_code/'

    for i in range(4000, 20000):
        data = json.dumps({"url": f"https://ssl{i}.com.ua/"})
        a = requests.post(url, data)
        time.sleep(0.1)
        print(i, a)


def pagination_test():
    count = 90
    max_count = 163
    page = 1
    count_of_pages = math.ceil(count / max_count)
    print(count_of_pages)

    if page <= count_of_pages:
        if not page == count_of_pages:
            right = page * max_count
            left = right - max_count
        else:
            right = count
            left = (page - 1) * max_count
    else:
        return []
