import urllib.request
import json

API_URL = "https://confident-cooperation-production.up.railway.app"
EMAIL = "buildwise2026x@gmail.com"
PASSWORD = "Buildwise2026"

def get_token():
    data = json.dumps({"email": EMAIL, "password": PASSWORD}).encode()
    req = urllib.request.Request(
        f"{API_URL}/api/v1/auth/login",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        body = json.loads(resp.read().decode())
        token = body["access_token"]
        print(f"Status: {resp.status}")
        print(f"Token OK: {token[:50]}...")
        return token
    except urllib.error.HTTPError as e:
        print(f"Status: {e.code}")
        print(f"Response: {e.read().decode()}")
        return None

if __name__ == "__main__":
    get_token()
