"""
BuildWise API Audit Agent — tests every module endpoint + E2E flows.
Run from Railway Console: python scripts/agent_audit.py
"""

import urllib.request
import json
import sys
from time import sleep

API = "https://confident-cooperation-production.up.railway.app"
EMAIL = "buildwise2026x@gmail.com"
PASSWORD = "Buildwise2026"
TOKEN = None

PASS = []
FAIL = []
WARN = []


def api(method, path, body=None, expect_204=False):
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        f"{API}{path}",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {TOKEN}",
        },
        method=method,
    )
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        if expect_204 or resp.status == 204:
            return {"_status": resp.status}
        result = json.loads(resp.read().decode())
        result["_status"] = resp.status
        return result
    except urllib.error.HTTPError as e:
        return {"_status": e.code, "_error": e.read().decode()[:300]}


def check(label, method, path, body=None, expect_204=False):
    result = api(method, path, body, expect_204)
    status = result.get("_status", 0)
    error = result.get("_error", "")

    if status >= 400:
        FAIL.append({"label": label, "path": f"{method} {path}", "status": status, "error": error})
        print(f"  ❌ {label} — HTTP {status}")
        return None

    data = result.get("data", result)
    meta = result.get("meta", {})
    total = meta.get("total", None)

    if isinstance(data, list) and len(data) == 0:
        WARN.append({"label": label, "path": f"{method} {path}", "reason": "empty list (0 records)"})
        print(f"  ⚠️  {label} — OK but empty (0 records)")
    elif isinstance(data, dict) and expect_204:
        print(f"  ✅ {label} — HTTP {status}")
    elif total is not None:
        print(f"  ✅ {label} — {total} records")
    else:
        count = len(data) if isinstance(data, list) else 1
        print(f"  ✅ {label} — OK ({count})")

    PASS.append({"label": label, "path": f"{method} {path}"})
    return data


def login():
    global TOKEN
    data = json.dumps({"email": EMAIL, "password": PASSWORD}).encode()
    req = urllib.request.Request(
        f"{API}/api/v1/auth/login",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        TOKEN = json.loads(resp.read().decode())["access_token"]
        PASS.append({"label": "Auth login", "path": "POST /api/v1/auth/login"})
        print("  ✅ Auth login — token OK")
        return True
    except urllib.error.HTTPError as e:
        FAIL.append({"label": "Auth login", "path": "POST /api/v1/auth/login", "status": e.code, "error": e.read().decode()[:200]})
        print(f"  ❌ Auth login — HTTP {e.code}")
        return False


# ═════════════════════════════════════════════════════════════════════════════
# AUDIT MODULES
# ═════════════════════════════════════════════════════════════════════════════

def audit_crm():
    print("\n── CRM ──")
    check("CRM Contacts", "GET", "/api/v1/crm/contacts")
    check("CRM Properties", "GET", "/api/v1/crm/properties")
    check("CRM Products", "GET", "/api/v1/crm/products")
    check("CRM Product Categories", "GET", "/api/v1/crm/product-categories")


def audit_pipeline():
    print("\n── Pipeline ──")
    check("Pipeline Opportunities", "GET", "/api/v1/pipeline/opportunities")
    check("Pipeline Offers", "GET", "/api/v1/pipeline/offers")
    check("Pipeline Contracts", "GET", "/api/v1/pipeline/contracts")
    check("Pipeline Activities", "GET", "/api/v1/pipeline/activities")
    check("Pipeline Kanban", "GET", "/api/v1/pipeline/kanban")
    check("Pipeline Forecast", "GET", "/api/v1/pipeline/forecast")


def audit_pm():
    print("\n── PM ──")
    projects = check("PM Projects", "GET", "/api/v1/pm/projects")
    if not projects:
        return

    for p in projects:
        pid = p["id"]
        name = p["name"][:30]
        check(f"PM WBS [{name}]", "GET", f"/api/v1/pm/projects/{pid}/wbs")
        check(f"PM Tasks [{name}]", "GET", f"/api/v1/pm/projects/{pid}/tasks")
        check(f"PM Timesheets [{name}]", "GET", f"/api/v1/pm/projects/{pid}/timesheets")
        check(f"PM Progress [{name}]", "GET", f"/api/v1/pm/projects/{pid}/progress")

        pct = p.get("percent_complete", 0)
        status = p.get("status", "?")
        if pct == 0 and status not in ("draft", "planning"):
            WARN.append({"label": f"PM Progress [{name}]", "path": "", "reason": f"percent_complete=0 but status={status}"})
            print(f"  ⚠️  {name} — percent_complete=0 but status={status}")


def audit_rm():
    print("\n── RM ──")
    check("RM Employees", "GET", "/api/v1/rm/employees")
    check("RM Equipment", "GET", "/api/v1/rm/equipment")
    check("RM Materials", "GET", "/api/v1/rm/materials")
    check("RM Allocations", "GET", "/api/v1/rm/allocations")


def audit_bi():
    print("\n── BI ──")
    check("BI KPI Definitions", "GET", "/api/v1/bi/kpis")
    check("BI Dashboards", "GET", "/api/v1/bi/dashboards")
    check("BI Executive Summary", "GET", "/api/v1/bi/executive-summary")
    check("BI Reports", "GET", "/api/v1/bi/reports")
    check("BI KPI Dashboard", "GET", "/api/v1/bi/kpi-dashboard")


def audit_system():
    print("\n── System ──")
    check("System Notifications", "GET", "/api/v1/system/notifications")
    check("GDPR Audit Trail", "GET", "/api/v1/gdpr/audit-trail")


# ═════════════════════════════════════════════════════════════════════════════
# E2E FLOWS
# ═════════════════════════════════════════════════════════════════════════════

def e2e_contact():
    print("\n── E2E: Contact CRUD ──")
    data = check("E2E Create Contact", "POST", "/api/v1/crm/contacts", {
        "contact_name": "__AUDIT_TEST__",
        "contact_type": "company",
        "email": "audit-test@example.com",
    })
    if not data:
        return

    cid = data.get("id")
    if not cid:
        FAIL.append({"label": "E2E Contact — no ID returned", "path": "", "status": 0, "error": "Missing id"})
        return

    check("E2E Read Contact", "GET", f"/api/v1/crm/contacts/{cid}")
    check("E2E Delete Contact", "DELETE", f"/api/v1/crm/contacts/{cid}", expect_204=True)

    verify = api("GET", f"/api/v1/crm/contacts/{cid}")
    if verify.get("_status") == 404:
        PASS.append({"label": "E2E Contact Deleted", "path": f"GET /api/v1/crm/contacts/{cid}"})
        print("  ✅ E2E Contact Deleted — 404 confirmed")
    else:
        WARN.append({"label": "E2E Contact Deleted", "path": "", "reason": f"Expected 404, got {verify.get('_status')}"})
        print(f"  ⚠️  E2E Contact Deleted — expected 404, got {verify.get('_status')} (soft delete?)")


def e2e_opportunity():
    print("\n── E2E: Opportunity CRUD ──")
    data = check("E2E Create Opportunity", "POST", "/api/v1/pipeline/opportunities", {
        "title": "__AUDIT_TEST_OPP__",
        "estimated_value": 1000.0,
        "stage": "new",
        "probability": 10,
    })
    if not data:
        return

    oid = data.get("id")
    if not oid:
        FAIL.append({"label": "E2E Opportunity — no ID", "path": "", "status": 0, "error": "Missing id"})
        return

    check("E2E Update Opportunity", "PUT", f"/api/v1/pipeline/opportunities/{oid}", {
        "stage": "qualified",
        "probability": 30,
    })
    check("E2E Delete Opportunity", "DELETE", f"/api/v1/pipeline/opportunities/{oid}", expect_204=True)


def e2e_project_progress():
    print("\n── E2E: Project Progress ──")
    projects = api("GET", "/api/v1/pm/projects?per_page=50")
    data = projects.get("data", projects) if isinstance(projects, dict) else projects

    if not data or not isinstance(data, list):
        FAIL.append({"label": "E2E Project Progress — no projects", "path": "GET /api/v1/pm/projects", "status": 0, "error": "No data"})
        print("  ❌ E2E Project Progress — no projects found")
        return

    bloc = None
    for p in data:
        if "Bloc A4" in p.get("name", ""):
            bloc = p
            break

    if not bloc:
        WARN.append({"label": "E2E Project Progress", "path": "", "reason": "Bloc A4 Iași not found"})
        print("  ⚠️  Bloc A4 Iași not found")
        return

    pct = bloc.get("percent_complete", 0)
    status = bloc.get("status", "?")

    if pct > 0:
        PASS.append({"label": "E2E Bloc A4 percent_complete > 0", "path": ""})
        print(f"  ✅ Bloc A4 percent_complete = {pct}%")
    else:
        FAIL.append({"label": "E2E Bloc A4 percent_complete", "path": "", "status": 0, "error": f"percent_complete={pct}, expected > 0"})
        print(f"  ❌ Bloc A4 percent_complete = {pct}% (expected > 0)")

    if status == "in_progress":
        PASS.append({"label": "E2E Bloc A4 status=in_progress", "path": ""})
        print(f"  ✅ Bloc A4 status = {status}")
    else:
        FAIL.append({"label": "E2E Bloc A4 status", "path": "", "status": 0, "error": f"status={status}, expected in_progress"})
        print(f"  ❌ Bloc A4 status = {status} (expected in_progress)")


# ═════════════════════════════════════════════════════════════════════════════
# REPORT
# ═════════════════════════════════════════════════════════════════════════════

def print_report():
    total = len(PASS) + len(FAIL)
    score = round(len(PASS) / total * 100, 1) if total > 0 else 0

    print("\n" + "═" * 60)
    print("  BUILDWISE API AUDIT REPORT")
    print("═" * 60)

    print(f"\n✅ FUNCȚIONEAZĂ ({len(PASS)}):")
    for p in PASS:
        print(f"   {p['label']}")

    if FAIL:
        print(f"\n❌ ERORI ({len(FAIL)}):")
        for f in FAIL:
            status = f"HTTP {f['status']}" if f['status'] else ""
            err = f.get('error', '')[:80]
            print(f"   {f['label']} — {status} {err}")

    if WARN:
        print(f"\n⚠️  AVERTISMENTE ({len(WARN)}):")
        for w in WARN:
            print(f"   {w['label']} — {w['reason']}")

    print(f"\n{'═' * 60}")
    print(f"  SCOR GENERAL: {score}% ({len(PASS)}/{total} endpoint-uri OK)")
    print(f"{'═' * 60}")

    if FAIL:
        print("\n  PRIORITATE FIX-URI:")
        critical = [f for f in FAIL if f.get("status") in (500, 502, 503)]
        important = [f for f in FAIL if f.get("status") in (401, 403, 404, 422)]
        minor = [f for f in FAIL if f not in critical and f not in important]

        idx = 1
        for f in critical:
            print(f"   {idx}. [CRITIC] {f['label']} — HTTP {f['status']}")
            idx += 1
        for f in important:
            print(f"   {idx}. [IMPORTANT] {f['label']} — HTTP {f['status']}")
            idx += 1
        for f in minor:
            print(f"   {idx}. [MINOR] {f['label']}")
            idx += 1

    print()


# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("═" * 60)
    print("  BUILDWISE API AUDIT AGENT")
    print("═" * 60)

    print("\n── Auth ──")
    if not login():
        print("\nCannot proceed without authentication.")
        sys.exit(1)

    audit_crm()
    audit_pipeline()
    audit_pm()
    audit_rm()
    audit_bi()
    audit_system()

    e2e_contact()
    e2e_opportunity()
    e2e_project_progress()

    print_report()
