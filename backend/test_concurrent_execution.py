
import getpass
from concurrent.futures import ThreadPoolExecutor
import urllib.request
import urllib.error
import json

BASE_URL = "http://127.0.0.1:8000"
APPROVAL_ID = 9

api_key = getpass.getpass("Enter Agent 11 API key: ")

def execute_request():
    url = f"{BASE_URL}/authorization/execute/{APPROVAL_ID}"

    request = urllib.request.Request(
        url,
        method="POST",
        headers={
            "X-Agent-API-Key": api_key,
            "Content-Type": "application/json"
        }
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, response.read().decode()

    except urllib.error.HTTPError as error:
        return error.code, error.read().decode()

    except Exception as error:
        return "ERROR", str(error)


print("\nSending two simultaneous execution requests...\n")

with ThreadPoolExecutor(max_workers=2) as executor:
    futures = [
        executor.submit(execute_request),
        executor.submit(execute_request)
    ]

    for index, future in enumerate(futures, start=1):
        status, response = future.result()
        print(f"Request {index} - HTTP {status}")
        print(response)
        print("-" * 50)
