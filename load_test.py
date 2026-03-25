import concurrent.futures
import requests
import time

BASE_URL = 'http://13.211.163.76:8080/api'

def make_request(i):
    start = time.time()
    resp = requests.get(f'{BASE_URL}/parcels')
    elapsed = time.time() - start
    return {'id': i, 'status': resp.status_code, 'time': round(elapsed, 3)}

with concurrent.futures.ThreadPoolExecutor(max_workers=20) as pool:
    results = list(pool.map(make_request, range(20)))

for r in results:
    print(f"Request {r['id']}: {r['status']} in {r['time']}s")


