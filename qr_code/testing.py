import requests
import json
import time
url = 'http://127.0.0.1:8000/qr_code/'


for i in range(4000, 20000):
    data = json.dumps({"url": f"https://ssl{i}.com.ua/"})
    a = requests.post(url, data)
    time.sleep(0.1)
    print(i, a)
