import requests
from concurrent.futures import ThreadPoolExecutor

PASTE_ID = "068cfcfd-2f9f-40df-abe2-ebafca3e41b4"
URL = f"http://127.0.0.1:5000/api/pastes/{PASTE_ID}"

def fetch_paste(_):
    response = requests.get(URL)
    return response.status_code

with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(fetch_paste, range(10)))

print("Successful requests (200):", results.count(200))
print("Unavailable requests (404):", results.count(404))
print("All status codes:", results)