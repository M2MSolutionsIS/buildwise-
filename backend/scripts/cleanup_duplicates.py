"""
Cleanup duplicate projects in BuildWise.
Run from Railway Console: python scripts/cleanup_duplicates.py
"""

import urllib.request
import json

API = "https://confident-cooperation-production.up.railway.app"
EMAIL = "buildwise2026x@gmail.com"
PASSWORD = "Buildwise2026"
TOKEN = None


def login():
    global TOKEN
    data = json.dumps({"email": EMAIL, "password": PASSWORD}).encode()
    req = urllib.request.Request(
        f"{API}/api/v1/auth/login",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    resp = urllib.request.urlopen(req, timeout=15)
    TOKEN = json.loads(resp.read().decode())["access_token"]
    print("Authenticated OK")


def get_projects():
    req = urllib.request.Request(
        f"{API}/api/v1/pm/projects?per_page=100",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {TOKEN}",
        },
    )
    resp = urllib.request.urlopen(req, timeout=30)
    result = json.loads(resp.read().decode())
    return result.get("data", [])


def delete_project(pid):
    req = urllib.request.Request(
        f"{API}/api/v1/pm/projects/{pid}",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {TOKEN}",
        },
        method="DELETE",
    )
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return resp.status
    except urllib.error.HTTPError as e:
        print(f"  ERROR {e.code} DELETE /api/v1/pm/projects/{pid}")
        return e.code


if __name__ == "__main__":
    login()

    projects = get_projects()
    print(f"\nFound {len(projects)} projects total:")
    for p in projects:
        print(f"  {p['id']} — {p['name']}")

    seen = {}
    duplicates = []
    for p in projects:
        name = p["name"]
        if name in seen:
            duplicates.append(p)
        else:
            seen[name] = p

    if not duplicates:
        print("\nNo duplicates found.")
    else:
        print(f"\n{len(duplicates)} duplicates to delete:")
        for p in duplicates:
            pid = p["id"]
            status = delete_project(pid)
            print(f"  DELETED {pid} — {p['name']} (HTTP {status})")
        print(f"\nDone. Kept {len(seen)} unique projects.")
