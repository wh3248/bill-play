import requests

def main():
    header = {}
    url = "https://hydrogen.princeton.edu/api/cog?email=wh3248@princeton.edu&pin=0000"
    with requests.get(url, stream=True, timeout=(3,30)) as r:
        print(r.status_code)
        first_bytes = r.raw.read(16*1024)
        print(len(first_bytes))
main()