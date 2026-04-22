import httpx
import json

API_URL = "https://confident-cooperation-production.up.railway.app"
EMAIL = "buildwise2026x@gmail.com"
PASSWORD = "Buildwise2026"

def get_token():
    resp = httpx.post(f"{API_URL}/api/v1/auth/login",
        json={"email": EMAIL, "password": PASSWORD})
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")
    if resp.status_code == 200:
        token = resp.json()["access_token"]
        print(f"Token OK: {token[:50]}...")
        return token
    return None

if __name__ == "__main__":
    get_token()
