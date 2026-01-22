import hf_hydrodata as hf
import requests
import time

def main():
    url = "https://hydrogen.princeton.edu/api/cog?email=wh3248@princeton.edu&pin=0000"
    start_timer = time.time()
    with requests.get(url, stream=True, timeout=(3,30)) as r:
        print(r.status_code)
        first_bytes = r.raw.read(16*1024)
        print("stream read duration", time.time() - start_timer)
        print(len(first_bytes))

    start_timer = time.time()
    header = {"Range": "bytes=0-16383"}
    response = requests.get(url, headers=header, timeout=3)
    print("range read duration", time.time() - start_timer)
    print("range status", response.status_code)
    print(len(response.content))

main()