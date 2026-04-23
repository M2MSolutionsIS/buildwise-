"""
BuildWise Demo Seed Data — all 3 prototypes (P1/P2/P3).
Run from Railway Console: python scripts/seed_demo_data.py
"""

import urllib.request
import json
import sys
from datetime import datetime, timedelta
from time import sleep

API = "https://confident-cooperation-production.up.railway.app"
EMAIL = "buildwise2026x@gmail.com"
PASSWORD = "Buildwise2026"
TOKEN = None


def api(method, path, body=None):
    for attempt in range(3):
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
            result = json.loads(resp.read().decode())
            return result.get("data", result)
        except urllib.error.HTTPError as e:
            if e.code in (502, 503) and attempt < 2:
                print(f"  RETRY {e.code} {method} {path} (attempt {attempt + 1}/3, waiting 5s...)")
                sleep(5)
                continue
            print(f"  ERROR {e.code} {method} {path}: {e.read().decode()[:200]}")
            return None


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
    print(f"Authenticated OK")


# ═════════════════════════════════════════════════════════════════════════════
# CRM — 15 Contacts, 8 Properties, 10 Products (F001-F012)
# ═════════════════════════════════════════════════════════════════════════════


def seed_crm():
    print("\n═══ CRM ═══")

    # ── 15 Contacts ──────────────────────────────────────────────────────────

    contacts_data = [
        {"company_name": "ThermoConstruct SRL", "cui": "RO12345678", "contact_type": "pj", "stage": "active", "city": "Iași", "county": "Iași", "phone": "0232100100", "email": "office@thermoconstruct.ro", "source": "referral", "tags": ["construcții", "reabilitare"], "vat_payer": True,
         "persons": [{"first_name": "Andrei", "last_name": "Popescu", "role": "Director General", "email": "andrei@thermoconstruct.ro", "phone": "0745100100", "is_primary": True}]},
        {"company_name": "Asociația de Proprietari Bloc A4 Iași", "cui": None, "contact_type": "pj", "stage": "active", "city": "Iași", "county": "Iași", "phone": "0232200200", "email": "blocA4@gmail.com", "source": "direct", "tags": ["asociație", "bloc"],
         "persons": [{"first_name": "Maria", "last_name": "Ionescu", "role": "Președinte", "email": "maria.ionescu@gmail.com", "phone": "0745200200", "is_primary": True}]},
        {"company_name": "Primăria Bacău — Direcția Investiții", "cui": "RO4278337", "contact_type": "pj", "stage": "active", "city": "Bacău", "county": "Bacău", "phone": "0234500500", "email": "investitii@primariabacau.ro", "source": "licitație", "tags": ["public", "educație"], "vat_payer": True,
         "persons": [{"first_name": "Ion", "last_name": "Munteanu", "role": "Director Investiții", "email": "ion.munteanu@primariabacau.ro", "phone": "0745300300", "is_primary": True}]},
        {"company_name": "Vila Popescu — Persoană Fizică", "cui": None, "contact_type": "pf", "stage": "active", "city": "Cluj-Napoca", "county": "Cluj", "phone": "0745400400", "email": "dan.popescu@yahoo.com", "source": "online",
         "persons": [{"first_name": "Dan", "last_name": "Popescu", "role": "Proprietar", "email": "dan.popescu@yahoo.com", "phone": "0745400400", "is_primary": True}]},
        {"company_name": "EcoInstal Pro SRL", "cui": "RO33445566", "contact_type": "pj", "stage": "active", "city": "București", "county": "București", "phone": "0212100100", "email": "contact@ecoinstal.ro", "source": "partener", "tags": ["HVAC", "instalații"], "vat_payer": True,
         "persons": [{"first_name": "Elena", "last_name": "Dumitrescu", "role": "Manager Tehnic", "email": "elena@ecoinstal.ro", "phone": "0745500500", "is_primary": True}]},
        {"company_name": "GreenBuild Materials SA", "cui": "RO11223344", "contact_type": "pj", "stage": "active", "city": "Timișoara", "county": "Timiș", "phone": "0256100100", "email": "vanzari@greenbuild.ro", "source": "furnizor", "tags": ["materiale", "izolații"], "vat_payer": True,
         "persons": [{"first_name": "Radu", "last_name": "Stancu", "role": "Director Vânzări", "email": "radu@greenbuild.ro", "phone": "0745600600", "is_primary": True}]},
        {"company_name": "Confort Urban SRL", "cui": "RO55667788", "contact_type": "imm", "stage": "potential_client", "city": "Constanța", "county": "Constanța", "phone": "0241100100", "email": "office@conforturban.ro", "source": "eveniment", "tags": ["construcții", "rezidențial"], "vat_payer": True,
         "persons": [{"first_name": "Mihai", "last_name": "Voiculescu", "role": "Administrator", "email": "mihai@conforturban.ro", "phone": "0745700700", "is_primary": True}]},
        {"company_name": "Asociația de Proprietari Bloc C2 Bacău", "cui": None, "contact_type": "pj", "stage": "prospect", "city": "Bacău", "county": "Bacău", "phone": "0234600600", "email": "blocc2bacau@gmail.com", "source": "referral", "tags": ["asociație", "bloc"],
         "persons": [{"first_name": "Vasile", "last_name": "Popa", "role": "Președinte", "email": "vasile.popa@gmail.com", "phone": "0745800800", "is_primary": True}]},
        {"company_name": "ArchiDesign Studio SRL", "cui": "RO99887766", "contact_type": "imm", "stage": "active", "city": "Brașov", "county": "Brașov", "phone": "0268100100", "email": "hello@archidesign.ro", "source": "partener", "tags": ["arhitectură", "proiectare"], "vat_payer": True,
         "persons": [{"first_name": "Cristina", "last_name": "Moldovan", "role": "Arhitect Șef", "email": "cristina@archidesign.ro", "phone": "0745900900", "is_primary": True}]},
        {"company_name": "FundConsult Engineering SRL", "cui": "RO66554433", "contact_type": "pj", "stage": "active", "city": "Iași", "county": "Iași", "phone": "0232300300", "email": "office@fundconsult.ro", "source": "referral", "tags": ["consultanță", "energie"], "vat_payer": True,
         "persons": [{"first_name": "Adrian", "last_name": "Neagu", "role": "Inginer Energetician", "email": "adrian@fundconsult.ro", "phone": "0746100100", "is_primary": True}]},
        {"company_name": "Renovare Express SRL", "cui": "RO22334455", "contact_type": "imm", "stage": "potential_client", "city": "Sibiu", "county": "Sibiu", "phone": "0269100100", "email": "contact@renovareexpress.ro", "source": "online", "tags": ["renovări", "rezidențial"], "vat_payer": True,
         "persons": [{"first_name": "Florin", "last_name": "Barbu", "role": "Director", "email": "florin@renovareexpress.ro", "phone": "0746200200", "is_primary": True}]},
        {"company_name": "SC Solar Panels Romania SRL", "cui": "RO44556677", "contact_type": "pj", "stage": "active", "city": "București", "county": "București", "phone": "0212200200", "email": "sales@solarpanels.ro", "source": "furnizor", "tags": ["solar", "energie verde"], "vat_payer": True,
         "persons": [{"first_name": "Oana", "last_name": "Radu", "role": "Manager Vânzări", "email": "oana@solarpanels.ro", "phone": "0746300300", "is_primary": True}]},
        {"company_name": "Habitat Construct SA", "cui": "RO77889900", "contact_type": "pj", "stage": "inactive", "city": "Galați", "county": "Galați", "phone": "0236100100", "email": "office@habitatconstruct.ro", "source": "licitație", "tags": ["construcții", "industrial"], "vat_payer": True,
         "persons": [{"first_name": "George", "last_name": "Dinu", "role": "Director Operațional", "email": "george@habitatconstruct.ro", "phone": "0746400400", "is_primary": True}]},
        {"company_name": "Smart Building Solutions SRL", "cui": "RO88990011", "contact_type": "imm", "stage": "prospect", "city": "Oradea", "county": "Bihor", "phone": "0259100100", "email": "info@smartbuilding.ro", "source": "online", "tags": ["smart home", "automatizări"],
         "persons": [{"first_name": "Laura", "last_name": "Nistor", "role": "CEO", "email": "laura@smartbuilding.ro", "phone": "0746500500", "is_primary": True}]},
        {"company_name": "Municipiul Iași — Direcția Tehnică", "cui": "RO4541580", "contact_type": "pj", "stage": "active", "city": "Iași", "county": "Iași", "phone": "0232400400", "email": "tehnic@primariaiasi.ro", "source": "licitație", "tags": ["public", "municipiu"], "vat_payer": True,
         "persons": [{"first_name": "Alexandru", "last_name": "Cojocaru", "role": "Director Tehnic", "email": "alex.cojocaru@primariaiasi.ro", "phone": "0746600600", "is_primary": True}]},
    ]

    contact_ids = []
    for c in contacts_data:
        result = api("POST", "/api/v1/crm/contacts", c)
        if result:
            cid = result.get("id", "?")
            contact_ids.append(cid)
            print(f"  Contact: {c['company_name']} → {cid}")
        else:
            contact_ids.append(None)

    # ── 3 Product Categories + 10 Products ───────────────────────────────────

    categories_data = [
        {"name": "Izolații Termice", "sort_order": 1},
        {"name": "Tâmplărie & Geamuri", "sort_order": 2},
        {"name": "Servicii Energetice", "sort_order": 3},
    ]

    cat_ids = []
    for cat in categories_data:
        result = api("POST", "/api/v1/crm/product-categories", cat)
        if result:
            cat_ids.append(result.get("id"))
            print(f"  Category: {cat['name']} → {result.get('id', '?')}")
        else:
            cat_ids.append(None)

    products_data = [
        {"name": "Polistiren expandat EPS 80 — 10cm", "code": "IZO-EPS-10", "product_type": "product", "unit_of_measure": "mp", "unit_price": 45.0, "vat_rate": 0.19, "category_id": cat_ids[0], "description": "Plăci polistiren expandat 10cm, densitate 15 kg/m³"},
        {"name": "Vată minerală bazaltică — 15cm", "code": "IZO-VMB-15", "product_type": "product", "unit_of_measure": "mp", "unit_price": 85.0, "vat_rate": 0.19, "category_id": cat_ids[0], "description": "Vată minerală bazaltică 15cm, λ=0.035 W/mK"},
        {"name": "Polistiren extrudat XPS — 8cm", "code": "IZO-XPS-08", "product_type": "product", "unit_of_measure": "mp", "unit_price": 72.0, "vat_rate": 0.19, "category_id": cat_ids[0], "description": "Plăci XPS 8cm pentru soclu și fundații"},
        {"name": "Tencuială decorativă siliconică", "code": "FIN-TDS-01", "product_type": "product", "unit_of_measure": "mp", "unit_price": 55.0, "vat_rate": 0.19, "category_id": cat_ids[0], "description": "Tencuială decorativă siliconică, granulație 1.5mm"},
        {"name": "Geam termoizolant tripan Low-E", "code": "TAM-GT3-01", "product_type": "product", "unit_of_measure": "mp", "unit_price": 320.0, "vat_rate": 0.19, "category_id": cat_ids[1], "description": "Geam tripan 4-16-4-16-4 Low-E, U=0.6 W/m²K"},
        {"name": "Fereastră PVC 5 camere — standard", "code": "TAM-PVC-5C", "product_type": "product", "unit_of_measure": "buc", "unit_price": 890.0, "vat_rate": 0.19, "category_id": cat_ids[1], "description": "Fereastră PVC 5 camere cu geam tripan, 120x140cm"},
        {"name": "Ușă intrare termoizolantă", "code": "TAM-UIT-01", "product_type": "product", "unit_of_measure": "buc", "unit_price": 2400.0, "vat_rate": 0.19, "category_id": cat_ids[1], "description": "Ușă metalică termoizolantă U=1.0 W/m²K"},
        {"name": "Audit energetic clădire rezidențială", "code": "SRV-AUD-RZ", "product_type": "service", "unit_of_measure": "buc", "unit_price": 3500.0, "vat_rate": 0.19, "category_id": cat_ids[2], "description": "Audit energetic complet conform Legea 372/2005"},
        {"name": "Certificat de performanță energetică", "code": "SRV-CPE-01", "product_type": "service", "unit_of_measure": "buc", "unit_price": 1200.0, "vat_rate": 0.19, "category_id": cat_ids[2], "description": "Emitere certificat energetic clădire"},
        {"name": "Proiectare reabilitare termică", "code": "SRV-PRT-01", "product_type": "service", "unit_of_measure": "buc", "unit_price": 8500.0, "vat_rate": 0.19, "category_id": cat_ids[2], "description": "Proiect tehnic complet reabilitare termică"},
    ]

    product_ids = []
    for p in products_data:
        result = api("POST", "/api/v1/crm/products", p)
        if result:
            product_ids.append(result.get("id"))
            print(f"  Product: {p['name']} → {result.get('id', '?')}")
        else:
            product_ids.append(None)

    # ── 8 Properties with Energy Profiles ────────────────────────────────────

    properties_specs = [
        {"contact_idx": 1, "name": "Bloc A4 — Str. Păcurari nr. 50, Iași", "property_type": "bloc_panou_prefabricat", "city": "Iași", "county": "Iași", "total_area_sqm": 4800.0, "heated_area_sqm": 4200.0, "floors_count": 10, "year_built": 1978, "structure_material": "Panou prefabricat BCA", "facade_material": "Panou prefabricat netermoizolat", "energy_class": "E",
         "energy": {"u_value_walls": 1.8, "u_value_roof": 2.1, "u_value_floor": 1.5, "u_value_windows": 3.5, "u_value_treated_glass": 0.3, "hvac_type": "Centrală termică pe gaz", "hvac_capacity_kw": 250.0, "hvac_efficiency": 0.78, "heating_source": "Gaz natural", "annual_consumption_kwh": 864000.0, "climate_zone": "III", "estimated_savings_kwh": 496800.0, "estimated_co2_reduction_kg": 99360.0}},
        {"contact_idx": 2, "name": "Școala Generală Nr. 5 Bacău", "property_type": "cladire_publica", "city": "Bacău", "county": "Bacău", "total_area_sqm": 2200.0, "heated_area_sqm": 1900.0, "floors_count": 3, "year_built": 1965, "structure_material": "Cărămidă", "facade_material": "Tencuială pe cărămidă", "energy_class": "F",
         "energy": {"u_value_walls": 2.2, "u_value_roof": 2.5, "u_value_floor": 1.8, "u_value_windows": 4.0, "hvac_type": "Centrală pe lemne + convectoare electrice", "hvac_capacity_kw": 120.0, "hvac_efficiency": 0.65, "heating_source": "Lemne + Electric", "annual_consumption_kwh": 396000.0, "climate_zone": "III", "estimated_savings_kwh": 237600.0, "estimated_co2_reduction_kg": 47520.0}},
        {"contact_idx": 3, "name": "Vila Popescu — Str. Eroilor 15, Cluj", "property_type": "casa_post_1990", "city": "Cluj-Napoca", "county": "Cluj", "total_area_sqm": 280.0, "heated_area_sqm": 250.0, "floors_count": 2, "year_built": 1995, "structure_material": "Cărămidă + BCA", "facade_material": "Tencuială", "energy_class": "D",
         "energy": {"u_value_walls": 1.2, "u_value_roof": 1.5, "u_value_floor": 1.0, "u_value_windows": 2.8, "hvac_type": "Centrală pe gaz condensare", "hvac_capacity_kw": 28.0, "hvac_efficiency": 0.88, "heating_source": "Gaz natural", "annual_consumption_kwh": 18200.0, "climate_zone": "II", "estimated_savings_kwh": 8190.0, "estimated_co2_reduction_kg": 1638.0}},
        {"contact_idx": 0, "name": "Depozit Industrial — Zona CUG, Iași", "property_type": "spatiu_industrial", "city": "Iași", "county": "Iași", "total_area_sqm": 1500.0, "heated_area_sqm": 800.0, "floors_count": 1, "year_built": 1985, "structure_material": "Metal + Panouri sandwich", "facade_material": "Tablă", "energy_class": "G",
         "energy": {"u_value_walls": 3.0, "u_value_roof": 3.2, "u_value_windows": 5.0, "hvac_type": "Aeroterme industriale", "hvac_capacity_kw": 180.0, "hvac_efficiency": 0.60, "heating_source": "Gaz natural", "annual_consumption_kwh": 270000.0, "climate_zone": "III", "estimated_savings_kwh": 162000.0, "estimated_co2_reduction_kg": 32400.0}},
        {"contact_idx": 7, "name": "Bloc C2 — Str. Republicii 22, Bacău", "property_type": "bloc_caramida", "city": "Bacău", "county": "Bacău", "total_area_sqm": 3200.0, "heated_area_sqm": 2800.0, "floors_count": 8, "year_built": 1970, "structure_material": "Cărămidă", "facade_material": "Tencuială degradată", "energy_class": "E",
         "energy": {"u_value_walls": 1.9, "u_value_roof": 2.0, "u_value_floor": 1.6, "u_value_windows": 3.8, "hvac_type": "Termoficare", "hvac_capacity_kw": 200.0, "hvac_efficiency": 0.72, "heating_source": "Termoficare", "annual_consumption_kwh": 576000.0, "climate_zone": "III", "estimated_savings_kwh": 345600.0, "estimated_co2_reduction_kg": 69120.0}},
        {"contact_idx": 6, "name": "Ansamblu Rezidențial Tomis Nord, Constanța", "property_type": "bloc_panou_prefabricat", "city": "Constanța", "county": "Constanța", "total_area_sqm": 6000.0, "heated_area_sqm": 5200.0, "floors_count": 12, "year_built": 1982, "structure_material": "Panou prefabricat", "facade_material": "Panou netermoizolat", "energy_class": "E",
         "energy": {"u_value_walls": 1.7, "u_value_roof": 1.9, "u_value_windows": 3.6, "hvac_type": "Termoficare + Convectoare", "hvac_capacity_kw": 350.0, "hvac_efficiency": 0.75, "heating_source": "Termoficare", "annual_consumption_kwh": 1080000.0, "climate_zone": "I", "estimated_savings_kwh": 594000.0, "estimated_co2_reduction_kg": 118800.0}},
        {"contact_idx": 14, "name": "Grădinița Nr. 12 — Iași", "property_type": "cladire_publica", "city": "Iași", "county": "Iași", "total_area_sqm": 650.0, "heated_area_sqm": 580.0, "floors_count": 2, "year_built": 1960, "structure_material": "Cărămidă", "facade_material": "Tencuială veche", "energy_class": "F",
         "energy": {"u_value_walls": 2.4, "u_value_roof": 2.8, "u_value_floor": 2.0, "u_value_windows": 4.2, "hvac_type": "Centrală pe gaz veche", "hvac_capacity_kw": 65.0, "hvac_efficiency": 0.62, "heating_source": "Gaz natural", "annual_consumption_kwh": 117000.0, "climate_zone": "III", "estimated_savings_kwh": 76050.0, "estimated_co2_reduction_kg": 15210.0}},
        {"contact_idx": 8, "name": "Clădire Birouri — Centrul Vechi, Brașov", "property_type": "cladire_comerciala", "city": "Brașov", "county": "Brașov", "total_area_sqm": 900.0, "heated_area_sqm": 780.0, "floors_count": 4, "year_built": 1935, "year_renovated": 2005, "structure_material": "Cărămidă interbelică", "facade_material": "Piatră + Tencuială", "energy_class": "D",
         "energy": {"u_value_walls": 1.4, "u_value_roof": 1.6, "u_value_windows": 2.5, "hvac_type": "VRV Multi-split", "hvac_capacity_kw": 85.0, "hvac_efficiency": 0.92, "heating_source": "Electric (pompă căldură)", "annual_consumption_kwh": 70200.0, "climate_zone": "II", "estimated_savings_kwh": 28080.0, "estimated_co2_reduction_kg": 5616.0}},
    ]

    property_ids = []
    for p in properties_specs:
        cidx = p["contact_idx"]
        if cidx >= len(contact_ids) or contact_ids[cidx] is None:
            print(f"  SKIP property {p['name']}: no contact")
            property_ids.append(None)
            continue

        energy = p.pop("energy")
        cidx = p.pop("contact_idx")
        yr = p.pop("year_renovated", None)
        prop_body = {**p, "contact_id": contact_ids[cidx]}
        if yr:
            prop_body["year_renovated"] = yr

        result = api("POST", f"/api/v1/crm/contacts/{contact_ids[cidx]}/properties", prop_body)
        if result:
            pid = result.get("id")
            property_ids.append(pid)
            print(f"  Property: {p['name']} → {pid}")
            api("PUT", f"/api/v1/crm/properties/{pid}/energy-profile", energy)
            print(f"    Energy profile set (U_walls={energy['u_value_walls']})")
        else:
            property_ids.append(None)

    return {
        "contact_ids": contact_ids,
        "product_ids": product_ids,
        "cat_ids": cat_ids,
        "property_ids": property_ids,
    }


# ═════════════════════════════════════════════════════════════════════════════
# PIPELINE — 12 Opportunities, 8 Offers, 4 Contracts, 20 Activities
# (F019, F026-F031, F042-F056)
# ═════════════════════════════════════════════════════════════════════════════


def seed_pipeline(crm):
    print("\n═══ PIPELINE ═══")
    cids = crm["contact_ids"]
    pids = crm["product_ids"]
    prop_ids = crm["property_ids"]

    now = datetime.utcnow()
    d = lambda days: (now + timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S")
    past = lambda days: (now - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S")

    # ── 12 Opportunities in diverse Kanban stages ────────────────────────────

    opps_data = [
        {"contact_id": cids[1], "title": "Reabilitare termică Bloc A4 Iași — fațadă + acoperiș", "stage": "won", "estimated_value": 485000.0, "expected_close_date": past(10), "source": "referral", "tags": ["reabilitare", "bloc"], "is_qualified": True},
        {"contact_id": cids[2], "title": "Izolare termică Școala Nr. 5 Bacău", "stage": "offering", "estimated_value": 320000.0, "expected_close_date": d(45), "source": "licitație", "tags": ["educație", "public"], "is_qualified": True},
        {"contact_id": cids[3], "title": "Renovare energetică Vila Popescu Cluj", "stage": "won", "estimated_value": 67000.0, "expected_close_date": past(90), "source": "online", "tags": ["rezidențial", "vilă"], "is_qualified": True},
        {"contact_id": cids[0], "title": "Termoizolare depozit industrial CUG Iași", "stage": "scoping", "estimated_value": 195000.0, "expected_close_date": d(60), "source": "direct", "tags": ["industrial"]},
        {"contact_id": cids[7], "title": "Reabilitare fațadă Bloc C2 Bacău", "stage": "qualified", "estimated_value": 290000.0, "expected_close_date": d(90), "source": "referral", "tags": ["bloc", "fațadă"]},
        {"contact_id": cids[6], "title": "Termoizolare ansamblu Tomis Nord Constanța", "stage": "new", "estimated_value": 720000.0, "expected_close_date": d(120), "source": "eveniment", "tags": ["bloc", "mare"]},
        {"contact_id": cids[14], "title": "Eficientizare energetică Grădinița Nr. 12 Iași", "stage": "sent", "estimated_value": 145000.0, "expected_close_date": d(30), "source": "licitație", "tags": ["public", "grădiniță"], "is_qualified": True},
        {"contact_id": cids[8], "title": "Renovare clădire birouri Centrul Vechi Brașov", "stage": "negotiation", "estimated_value": 210000.0, "expected_close_date": d(20), "source": "partener", "tags": ["birouri", "renovare"], "is_qualified": True},
        {"contact_id": cids[10], "title": "Izolare termică bloc rezidențial Sibiu", "stage": "qualified", "estimated_value": 380000.0, "expected_close_date": d(75), "source": "online", "tags": ["rezidențial"]},
        {"contact_id": cids[13], "title": "Automatizare HVAC clădire smart Oradea", "stage": "new", "estimated_value": 95000.0, "expected_close_date": d(100), "source": "online", "tags": ["smart", "HVAC"]},
        {"contact_id": cids[12], "title": "Reabilitare hală industrială Galați", "stage": "lost", "estimated_value": 430000.0, "expected_close_date": past(30), "source": "licitație", "tags": ["industrial", "hală"]},
        {"contact_id": cids[4], "title": "Instalare panouri solare + pompă căldură — pachet", "stage": "scoping", "estimated_value": 52000.0, "expected_close_date": d(55), "source": "partener", "tags": ["solar", "pompă căldură"]},
    ]

    opp_ids = []
    for o in opps_data:
        result = api("POST", "/api/v1/pipeline/opportunities", o)
        if result:
            oid = result.get("id", "?")
            opp_ids.append(oid)
            print(f"  Opportunity [{o['stage']}]: {o['title'][:50]}... → {oid}")
        else:
            opp_ids.append(None)

    # ── 8 Offers (draft, sent, accepted, rejected) ──────────────────────────

    offers_data = [
        {"contact_id": cids[1], "opportunity_id": opp_ids[0], "property_id": prop_ids[0], "title": "Ofertă reabilitare termică Bloc A4 Iași — v2", "description": "Izolare fațadă EPS 15cm + înlocuire tâmplărie + izolare acoperiș", "validity_days": 30,
         "line_items": [
             {"description": "Termoizolație fațadă EPS 80 — 15cm", "quantity": 2800.0, "unit_price": 65.0, "unit_of_measure": "mp", "vat_rate": 0.19, "sort_order": 1},
             {"description": "Înlocuire tâmplărie PVC 5 camere", "quantity": 120.0, "unit_price": 890.0, "unit_of_measure": "buc", "vat_rate": 0.19, "sort_order": 2},
             {"description": "Termoizolație acoperiș vată minerală 20cm", "quantity": 480.0, "unit_price": 95.0, "unit_of_measure": "mp", "vat_rate": 0.19, "sort_order": 3},
             {"description": "Manoperă montaj + schele", "quantity": 1.0, "unit_price": 148400.0, "unit_of_measure": "forfait", "vat_rate": 0.19, "sort_order": 4},
         ]},
        {"contact_id": cids[2], "opportunity_id": opp_ids[1], "property_id": prop_ids[1], "title": "Ofertă izolare Școala Nr. 5 Bacău", "description": "Izolare completă fațadă + acoperiș + ferestre", "validity_days": 45,
         "line_items": [
             {"description": "Termoizolație fațadă vată minerală 15cm", "quantity": 1400.0, "unit_price": 85.0, "unit_of_measure": "mp", "vat_rate": 0.19, "sort_order": 1},
             {"description": "Înlocuire ferestre PVC tripan", "quantity": 65.0, "unit_price": 920.0, "unit_of_measure": "buc", "vat_rate": 0.19, "sort_order": 2},
             {"description": "Izolare acoperiș tip terasă", "quantity": 750.0, "unit_price": 72.0, "unit_of_measure": "mp", "vat_rate": 0.19, "sort_order": 3},
         ]},
        {"contact_id": cids[3], "opportunity_id": opp_ids[2], "property_id": prop_ids[2], "title": "Ofertă renovare energetică Vila Popescu", "description": "Izolare fațadă + tâmplărie + certificat energetic", "validity_days": 30,
         "line_items": [
             {"description": "Izolare fațadă EPS 10cm", "quantity": 320.0, "unit_price": 55.0, "unit_of_measure": "mp", "vat_rate": 0.19, "sort_order": 1},
             {"description": "Ferestre PVC 5 camere", "quantity": 12.0, "unit_price": 890.0, "unit_of_measure": "buc", "vat_rate": 0.19, "sort_order": 2},
             {"description": "Certificat performanță energetică", "quantity": 1.0, "unit_price": 1200.0, "unit_of_measure": "buc", "vat_rate": 0.19, "sort_order": 3},
         ]},
        {"contact_id": cids[14], "opportunity_id": opp_ids[6], "property_id": prop_ids[6], "title": "Ofertă eficientizare Grădinița Nr. 12 Iași", "description": "Izolare completă + HVAC nou", "validity_days": 30,
         "line_items": [
             {"description": "Izolare fațadă vată bazaltică 12cm", "quantity": 420.0, "unit_price": 78.0, "unit_of_measure": "mp", "vat_rate": 0.19, "sort_order": 1},
             {"description": "Centrală termică condensare 80kW", "quantity": 1.0, "unit_price": 18500.0, "unit_of_measure": "buc", "vat_rate": 0.19, "sort_order": 2},
             {"description": "Manoperă instalare", "quantity": 1.0, "unit_price": 35000.0, "unit_of_measure": "forfait", "vat_rate": 0.19, "sort_order": 3},
         ]},
        {"contact_id": cids[8], "opportunity_id": opp_ids[7], "property_id": prop_ids[7], "title": "Ofertă renovare birouri Brașov — Centrul Vechi", "description": "Izolare interior + tâmplărie lemn stratificat + HVAC upgrade", "validity_days": 30,
         "line_items": [
             {"description": "Izolare interioară cu plăci PIR 8cm", "quantity": 600.0, "unit_price": 110.0, "unit_of_measure": "mp", "vat_rate": 0.19, "sort_order": 1},
             {"description": "Tâmplărie lemn stratificat tripan", "quantity": 35.0, "unit_price": 1800.0, "unit_of_measure": "buc", "vat_rate": 0.19, "sort_order": 2},
             {"description": "Upgrade VRV + automatizare BMS", "quantity": 1.0, "unit_price": 42000.0, "unit_of_measure": "forfait", "vat_rate": 0.19, "sort_order": 3},
         ]},
        {"contact_id": cids[0], "opportunity_id": opp_ids[3], "property_id": prop_ids[3], "title": "Ofertă termoizolare depozit CUG Iași", "description": "Panouri sandwich + acoperiș", "validity_days": 45,
         "line_items": [
             {"description": "Panouri sandwich 10cm fațadă", "quantity": 900.0, "unit_price": 120.0, "unit_of_measure": "mp", "vat_rate": 0.19, "sort_order": 1},
             {"description": "Izolare acoperiș hală — vată minerală", "quantity": 1500.0, "unit_price": 65.0, "unit_of_measure": "mp", "vat_rate": 0.19, "sort_order": 2},
         ]},
        {"contact_id": cids[12], "opportunity_id": opp_ids[10], "title": "Ofertă reabilitare hală Galați — respinsă", "description": "Ofertă respinsă — preț prea mare vs. buget", "validity_days": 30,
         "line_items": [
             {"description": "Termoizolație completă hală", "quantity": 1.0, "unit_price": 430000.0, "unit_of_measure": "forfait", "vat_rate": 0.19, "sort_order": 1},
         ]},
        {"contact_id": cids[4], "opportunity_id": opp_ids[11], "title": "Ofertă panouri solare + pompă căldură", "description": "Pachet complet: 20 panouri + pompă căldură aer-apă", "validity_days": 30, "is_quick_quote": True,
         "line_items": [
             {"description": "Panouri fotovoltaice 450W monocristalin", "quantity": 20.0, "unit_price": 850.0, "unit_of_measure": "buc", "vat_rate": 0.19, "sort_order": 1},
             {"description": "Pompă căldură aer-apă 12kW", "quantity": 1.0, "unit_price": 15200.0, "unit_of_measure": "buc", "vat_rate": 0.19, "sort_order": 2},
             {"description": "Montaj + cablare + PIF", "quantity": 1.0, "unit_price": 8500.0, "unit_of_measure": "forfait", "vat_rate": 0.19, "sort_order": 3},
         ]},
    ]

    offer_ids = []
    for o in offers_data:
        result = api("POST", "/api/v1/pipeline/offers", o)
        if result:
            oid = result.get("id", "?")
            offer_ids.append(oid)
            print(f"  Offer: {o['title'][:55]}... → {oid}")
        else:
            offer_ids.append(None)

    # ── 4 Contracts (2 active, 1 signed, 1 completed) ───────────────────────

    contracts_data = [
        {"contact_id": cids[1], "offer_id": offer_ids[0], "opportunity_id": opp_ids[0], "title": "Contract reabilitare termică Bloc A4 Iași", "total_value": 485000.0, "start_date": past(60), "end_date": d(120), "terms_and_conditions": "Garanție 5 ani lucrări fațadă, 10 ani tâmplărie. Plata în 4 tranșe."},
        {"contact_id": cids[3], "offer_id": offer_ids[2], "opportunity_id": opp_ids[2], "title": "Contract renovare energetică Vila Popescu", "total_value": 67000.0, "start_date": past(150), "end_date": past(30), "terms_and_conditions": "Garanție 3 ani. Plata 50% avans + 50% recepție."},
        {"contact_id": cids[8], "offer_id": offer_ids[4], "opportunity_id": opp_ids[7], "title": "Contract renovare birouri Centrul Vechi Brașov", "total_value": 210000.0, "start_date": d(15), "end_date": d(180), "terms_and_conditions": "Lucrări conform autorizație ISC. Garanție 5 ani."},
        {"contact_id": cids[14], "offer_id": offer_ids[3], "opportunity_id": opp_ids[6], "title": "Contract eficientizare Grădinița Nr. 12 Iași", "total_value": 145000.0, "start_date": d(30), "end_date": d(210), "terms_and_conditions": "Plata din fonduri publice — conform HG. Garanție 10 ani."},
    ]

    contract_ids = []
    for c in contracts_data:
        result = api("POST", "/api/v1/pipeline/contracts", c)
        if result:
            cid = result.get("id", "?")
            contract_ids.append(cid)
            print(f"  Contract: {c['title'][:55]}... → {cid}")
        else:
            contract_ids.append(None)

    # Sign first 2 contracts (Bloc A4 = active, Vila Popescu = completed)
    if contract_ids[0]:
        api("POST", f"/api/v1/pipeline/contracts/{contract_ids[0]}/sign", {"signed_date": past(58)})
        print(f"    Signed: Bloc A4 Iași")
    if contract_ids[1]:
        api("POST", f"/api/v1/pipeline/contracts/{contract_ids[1]}/sign", {"signed_date": past(148)})
        print(f"    Signed: Vila Popescu")
    if contract_ids[2]:
        api("POST", f"/api/v1/pipeline/contracts/{contract_ids[2]}/sign", {"signed_date": past(2)})
        print(f"    Signed: Birouri Brașov")

    # ── 20 Activities (calls, visits, emails, meetings, follow-ups) ──────────

    activities_data = [
        {"activity_type": "call", "title": "Apel inițial — prezentare servicii", "contact_id": cids[1], "opportunity_id": opp_ids[0], "scheduled_date": past(180), "duration_minutes": 25, "call_duration_seconds": 1500, "call_outcome": "Interesat, solicită vizită tehnică", "notes": "Contact cald, are fonduri aprobate"},
        {"activity_type": "technical_visit", "title": "Vizită tehnică Bloc A4 — măsurători fațadă", "contact_id": cids[1], "opportunity_id": opp_ids[0], "scheduled_date": past(170), "duration_minutes": 180, "visit_data": {"location": "Str. Păcurari 50, Iași", "attendees": ["Andrei Popescu", "Tehnician BAHM"]}, "measurements": {"facade_sqm": 2800, "windows_count": 120, "roof_sqm": 480}, "notes": "Stare avansată de degradare fațadă nord"},
        {"activity_type": "email", "title": "Trimitere ofertă Bloc A4 — v2 finală", "contact_id": cids[1], "opportunity_id": opp_ids[0], "scheduled_date": past(120), "duration_minutes": 10, "email_subject": "Ofertă reabilitare termică Bloc A4 — versiune finală", "email_tracked": True},
        {"activity_type": "meeting", "title": "Întâlnire negociere Bloc A4 — Asociație", "contact_id": cids[1], "opportunity_id": opp_ids[0], "scheduled_date": past(90), "duration_minutes": 90, "notes": "Negociere preț final, reducere 3% acceptată. Semnare săptămâna viitoare."},
        {"activity_type": "call", "title": "Apel Primăria Bacău — Școala Nr. 5", "contact_id": cids[2], "opportunity_id": opp_ids[1], "scheduled_date": past(45), "duration_minutes": 35, "call_duration_seconds": 2100, "call_outcome": "Solicită ofertă detaliată, au buget aprobat"},
        {"activity_type": "technical_visit", "title": "Vizită tehnică Școala Nr. 5 Bacău", "contact_id": cids[2], "opportunity_id": opp_ids[1], "scheduled_date": past(35), "duration_minutes": 240, "visit_data": {"location": "Str. Mărășești 12, Bacău", "attendees": ["Ion Munteanu", "Echipa BAHM"]}, "measurements": {"facade_sqm": 1400, "windows_count": 65, "roof_sqm": 750}},
        {"activity_type": "email", "title": "Trimitere ofertă Școala Bacău", "contact_id": cids[2], "opportunity_id": opp_ids[1], "scheduled_date": past(20), "duration_minutes": 15, "email_subject": "Ofertă eficientizare energetică Școala Nr. 5 Bacău", "email_tracked": True},
        {"activity_type": "follow_up", "title": "Follow-up ofertă Școala — așteptăm răspuns", "contact_id": cids[2], "opportunity_id": opp_ids[1], "scheduled_date": past(7), "duration_minutes": 10, "notes": "Comisia analizează, răspuns în 2 săptămâni"},
        {"activity_type": "call", "title": "Apel Vila Popescu — confirmare finalizare", "contact_id": cids[3], "opportunity_id": opp_ids[2], "scheduled_date": past(35), "duration_minutes": 15, "call_duration_seconds": 900, "call_outcome": "Lucrări finalizate, programare recepție"},
        {"activity_type": "meeting", "title": "Recepție finală Vila Popescu", "contact_id": cids[3], "opportunity_id": opp_ids[2], "scheduled_date": past(28), "duration_minutes": 120, "notes": "Recepție fără observații. Client foarte mulțumit, solicită certificat energetic."},
        {"activity_type": "call", "title": "Apel depozit CUG — evaluare preliminară", "contact_id": cids[0], "opportunity_id": opp_ids[3], "scheduled_date": past(15), "duration_minutes": 20, "call_duration_seconds": 1200, "call_outcome": "Interesat, programare vizită"},
        {"activity_type": "technical_visit", "title": "Vizită tehnică depozit CUG Iași", "contact_id": cids[0], "opportunity_id": opp_ids[3], "scheduled_date": past(8), "duration_minutes": 150, "visit_data": {"location": "Zona CUG, Iași", "attendees": ["Andrei Popescu (ThermoConstruct)", "Echipa BAHM"]}, "measurements": {"facade_sqm": 900, "roof_sqm": 1500}},
        {"activity_type": "call", "title": "Apel Bloc C2 Bacău — calificare", "contact_id": cids[7], "opportunity_id": opp_ids[4], "scheduled_date": past(25), "duration_minutes": 30, "call_duration_seconds": 1800, "call_outcome": "Asociație interesată, buget limitat"},
        {"activity_type": "email", "title": "Email informativ Tomis Nord Constanța", "contact_id": cids[6], "opportunity_id": opp_ids[5], "scheduled_date": past(5), "duration_minutes": 20, "email_subject": "Prezentare servicii reabilitare termică — BAHM", "email_tracked": True},
        {"activity_type": "follow_up", "title": "Follow-up birouri Brașov — negociere finală", "contact_id": cids[8], "opportunity_id": opp_ids[7], "scheduled_date": past(5), "duration_minutes": 45, "notes": "Negociere finalizată, se pregătește contractul"},
        {"activity_type": "call", "title": "Apel Grădinița Nr. 12 — clarificări ofertă", "contact_id": cids[14], "opportunity_id": opp_ids[6], "scheduled_date": past(12), "duration_minutes": 20, "call_duration_seconds": 1200, "call_outcome": "Solicită detalii HVAC, trimitem specificații"},
        {"activity_type": "email", "title": "Trimitere specificații HVAC Grădinița 12", "contact_id": cids[14], "opportunity_id": opp_ids[6], "scheduled_date": past(10), "duration_minutes": 30, "email_subject": "Specificații tehnice centrală termică condensare 80kW", "email_tracked": True},
        {"activity_type": "call", "title": "Apel Smart Building Oradea — prospect nou", "contact_id": cids[13], "opportunity_id": opp_ids[9], "scheduled_date": past(3), "duration_minutes": 25, "call_duration_seconds": 1500, "call_outcome": "Interesat de automatizare HVAC, solicită prezentare"},
        {"activity_type": "follow_up", "title": "Follow-up panouri solare EcoInstal", "contact_id": cids[4], "opportunity_id": opp_ids[11], "scheduled_date": d(3), "duration_minutes": 15, "notes": "De trimis ofertă finală cu specificații panouri monocristalin"},
        {"activity_type": "meeting", "title": "Întâlnire planificare Q2 — review pipeline", "scheduled_date": d(7), "duration_minutes": 60, "notes": "Review pipeline Q2: 12 oportunități active, forecast 2.4M RON"},
    ]

    act_ids = []
    for a in activities_data:
        result = api("POST", "/api/v1/pipeline/activities", a)
        if result:
            aid = result.get("id", "?")
            act_ids.append(aid)
            print(f"  Activity [{a['activity_type']}]: {a['title'][:50]}...")
        else:
            act_ids.append(None)

    return {
        "opp_ids": opp_ids,
        "offer_ids": offer_ids,
        "contract_ids": contract_ids,
        "act_ids": act_ids,
    }


# ═════════════════════════════════════════════════════════════════════════════
# PM — 3 Projects, WBS, Tasks, Timesheets, Energy Impact (F063-F088)
# ═════════════════════════════════════════════════════════════════════════════


def seed_pm(crm, pipe):
    print("\n═══ PM ═══")
    cids = crm["contact_ids"]
    prop_ids = crm["property_ids"]
    contract_ids = pipe["contract_ids"]

    now = datetime.utcnow()
    d = lambda days: (now + timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S")
    past = lambda days: (now - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S")

    # ── 3 Projects ───────────────────────────────────────────────────────────

    projects_data = [
        {
            "project_number": "PRJ-2025-001",
            "name": "Reabilitare termică Bloc A4 Iași",
            "description": "Reabilitare completă: fațadă EPS 15cm, tâmplărie PVC, acoperiș vată minerală. PRE: 180 kWh/m²/an → POST target: 65 kWh/m²/an",
            "project_type": "client",
            "contact_id": cids[1],
            "contract_id": contract_ids[0],
            "planned_start_date": past(55),
            "planned_end_date": d(120),
            "budget_allocated": 485000.0,
            "tags": ["reabilitare", "bloc", "energie"],
        },
        {
            "project_number": "PRJ-2025-002",
            "name": "Izolare termică Școala Nr. 5 Bacău",
            "description": "Izolare fațadă vată minerală 15cm + ferestre PVC + acoperiș. Faza de planificare.",
            "project_type": "client",
            "contact_id": cids[2],
            "planned_start_date": d(30),
            "planned_end_date": d(210),
            "budget_allocated": 320000.0,
            "tags": ["educație", "public", "planificare"],
        },
        {
            "project_number": "PRJ-2024-015",
            "name": "Renovare energetică Vila Popescu",
            "description": "Izolare fațadă EPS 10cm + tâmplărie PVC + certificat energetic. Proiect finalizat cu succes.",
            "project_type": "client",
            "contact_id": cids[3],
            "contract_id": contract_ids[1],
            "planned_start_date": past(150),
            "planned_end_date": past(30),
            "budget_allocated": 67000.0,
            "tags": ["rezidențial", "vilă", "finalizat"],
        },
    ]

    project_ids = []
    for p in projects_data:
        result = api("POST", "/api/v1/pm/projects", p)
        if result:
            pid = result.get("id", "?")
            project_ids.append(pid)
            print(f"  Project: {p['name']} → {pid}")
        else:
            project_ids.append(None)

    # ── WBS for Project 1: Bloc A4 Iași (in execution) ───────────────────────

    wbs_bloc = [
        {"code": "C01", "name": "Pregătire și organizare șantier", "node_type": "chapter", "sort_order": 1, "level": 0, "budget_allocated": 28000.0},
        {"code": "C02", "name": "Termoizolație fațadă", "node_type": "chapter", "sort_order": 2, "level": 0, "budget_allocated": 210000.0},
        {"code": "C02.1", "name": "Montaj schelă fațadă", "node_type": "subchapter", "sort_order": 1, "level": 1, "budget_allocated": 35000.0},
        {"code": "C02.2", "name": "Aplicare EPS 15cm + tencuială", "node_type": "subchapter", "sort_order": 2, "level": 1, "budget_allocated": 140000.0},
        {"code": "C02.3", "name": "Finisaje fațadă siliconică", "node_type": "subchapter", "sort_order": 3, "level": 1, "budget_allocated": 35000.0},
        {"code": "C03", "name": "Înlocuire tâmplărie PVC", "node_type": "chapter", "sort_order": 3, "level": 0, "budget_allocated": 106800.0},
        {"code": "C04", "name": "Termoizolație acoperiș", "node_type": "chapter", "sort_order": 4, "level": 0, "budget_allocated": 45600.0},
        {"code": "C05", "name": "Recepție și predare", "node_type": "chapter", "sort_order": 5, "level": 0, "budget_allocated": 12000.0},
    ]

    wbs_ids_bloc = []
    if project_ids[0]:
        parent_map = {}
        for w in wbs_bloc:
            result = api("POST", f"/api/v1/pm/projects/{project_ids[0]}/wbs", w)
            if result:
                wid = result.get("id")
                wbs_ids_bloc.append(wid)
                parent_map[w["code"]] = wid
                print(f"    WBS [{w['code']}]: {w['name']}")
            else:
                wbs_ids_bloc.append(None)

        # Link subchapters to parent C02
        c02_id = parent_map.get("C02")
        for sub_code in ["C02.1", "C02.2", "C02.3"]:
            sub_id = parent_map.get(sub_code)
            if sub_id and c02_id:
                api("PUT", f"/api/v1/pm/wbs/{sub_id}", {"parent_id": c02_id})

    # ── Tasks for Project 1 ──────────────────────────────────────────────────

    tasks_bloc = [
        {"title": "Instalare garduri protecție și semnalizare", "planned_start": past(55), "planned_end": past(50), "estimated_hours": 40, "status": "done", "wbs_node_id": wbs_ids_bloc[0] if wbs_ids_bloc else None},
        {"title": "Montaj schelă metalică fațadă nord + est", "planned_start": past(50), "planned_end": past(40), "estimated_hours": 120, "status": "done", "wbs_node_id": wbs_ids_bloc[2] if len(wbs_ids_bloc) > 2 else None},
        {"title": "Curățare și grunduire fațadă nord", "planned_start": past(40), "planned_end": past(35), "estimated_hours": 80, "status": "done", "wbs_node_id": wbs_ids_bloc[3] if len(wbs_ids_bloc) > 3 else None},
        {"title": "Lipire plăci EPS 15cm — fațadă nord", "planned_start": past(35), "planned_end": past(20), "estimated_hours": 200, "status": "done", "wbs_node_id": wbs_ids_bloc[3] if len(wbs_ids_bloc) > 3 else None},
        {"title": "Lipire plăci EPS 15cm — fațadă est", "planned_start": past(20), "planned_end": past(5), "estimated_hours": 180, "status": "in_progress", "wbs_node_id": wbs_ids_bloc[3] if len(wbs_ids_bloc) > 3 else None},
        {"title": "Aplicare tencuială decorativă siliconică", "planned_start": d(5), "planned_end": d(25), "estimated_hours": 160, "status": "todo", "wbs_node_id": wbs_ids_bloc[4] if len(wbs_ids_bloc) > 4 else None},
        {"title": "Demontare ferestre vechi + montaj PVC", "planned_start": past(15), "planned_end": d(30), "estimated_hours": 320, "status": "in_progress", "wbs_node_id": wbs_ids_bloc[5] if len(wbs_ids_bloc) > 5 else None},
        {"title": "Termoizolație acoperiș — vată minerală 20cm", "planned_start": d(20), "planned_end": d(50), "estimated_hours": 140, "status": "todo", "wbs_node_id": wbs_ids_bloc[6] if len(wbs_ids_bloc) > 6 else None},
        {"title": "Verificări finale și recepție", "planned_start": d(100), "planned_end": d(115), "estimated_hours": 60, "status": "todo", "is_milestone": True, "wbs_node_id": wbs_ids_bloc[7] if len(wbs_ids_bloc) > 7 else None},
    ]

    task_ids_bloc = []
    if project_ids[0]:
        for t in tasks_bloc:
            body = {k: v for k, v in t.items() if v is not None}
            result = api("POST", f"/api/v1/pm/projects/{project_ids[0]}/tasks", body)
            if result:
                tid = result.get("id")
                task_ids_bloc.append(tid)
                print(f"    Task [{t.get('status','todo')}]: {t['title'][:50]}...")
            else:
                task_ids_bloc.append(None)

    # ── WBS for Project 2: Școala Bacău (planning) ───────────────────────────

    wbs_scoala = [
        {"code": "S01", "name": "Proiectare și avize", "node_type": "chapter", "sort_order": 1, "level": 0, "budget_allocated": 25000.0},
        {"code": "S02", "name": "Izolare fațadă", "node_type": "chapter", "sort_order": 2, "level": 0, "budget_allocated": 135000.0},
        {"code": "S03", "name": "Înlocuire ferestre", "node_type": "chapter", "sort_order": 3, "level": 0, "budget_allocated": 65000.0},
        {"code": "S04", "name": "Izolare acoperiș terasă", "node_type": "chapter", "sort_order": 4, "level": 0, "budget_allocated": 60000.0},
        {"code": "S05", "name": "Recepție și certificare", "node_type": "chapter", "sort_order": 5, "level": 0, "budget_allocated": 15000.0},
    ]

    if project_ids[1]:
        for w in wbs_scoala:
            result = api("POST", f"/api/v1/pm/projects/{project_ids[1]}/wbs", w)
            if result:
                print(f"    WBS [{w['code']}]: {w['name']}")

        tasks_scoala = [
            {"title": "Elaborare proiect tehnic", "planned_start": d(30), "planned_end": d(60), "estimated_hours": 120, "status": "todo"},
            {"title": "Obținere autorizație ISC", "planned_start": d(60), "planned_end": d(80), "estimated_hours": 40, "status": "todo"},
            {"title": "Licitație materiale izolare", "planned_start": d(70), "planned_end": d(85), "estimated_hours": 30, "status": "todo"},
        ]
        for t in tasks_scoala:
            api("POST", f"/api/v1/pm/projects/{project_ids[1]}/tasks", t)
            print(f"    Task [todo]: {t['title']}")

    # ── WBS for Project 3: Vila Popescu (completed) ──────────────────────────

    wbs_vila = [
        {"code": "V01", "name": "Izolare fațadă EPS 10cm", "node_type": "chapter", "sort_order": 1, "level": 0, "budget_allocated": 20000.0},
        {"code": "V02", "name": "Înlocuire tâmplărie", "node_type": "chapter", "sort_order": 2, "level": 0, "budget_allocated": 12000.0},
        {"code": "V03", "name": "Certificare energetică", "node_type": "chapter", "sort_order": 3, "level": 0, "budget_allocated": 1500.0},
    ]

    if project_ids[2]:
        for w in wbs_vila:
            api("POST", f"/api/v1/pm/projects/{project_ids[2]}/wbs", w)
            print(f"    WBS [{w['code']}]: {w['name']}")

        tasks_vila = [
            {"title": "Montaj EPS 10cm fațadă completă", "planned_start": past(140), "planned_end": past(100), "estimated_hours": 80, "status": "done"},
            {"title": "Montaj ferestre PVC 5 camere", "planned_start": past(100), "planned_end": past(80), "estimated_hours": 48, "status": "done"},
            {"title": "Tencuială decorativă", "planned_start": past(80), "planned_end": past(60), "estimated_hours": 40, "status": "done"},
            {"title": "Emitere certificat energetic", "planned_start": past(50), "planned_end": past(40), "estimated_hours": 16, "status": "done"},
        ]
        for t in tasks_vila:
            api("POST", f"/api/v1/pm/projects/{project_ids[2]}/tasks", t)
            print(f"    Task [done]: {t['title']}")

    # ── Timesheets for Project 1 (Bloc A4 — in execution) ────────────────────

    if project_ids[0] and task_ids_bloc:
        timesheets = [
            {"task_id": task_ids_bloc[0], "work_date": past(53), "hours": 8.0, "description": "Instalare gard perimetral nord"},
            {"task_id": task_ids_bloc[0], "work_date": past(52), "hours": 8.0, "description": "Instalare gard est + semnalizare"},
            {"task_id": task_ids_bloc[1], "work_date": past(48), "hours": 10.0, "description": "Montaj schelă etaj 1-3 fațadă nord"},
            {"task_id": task_ids_bloc[1], "work_date": past(47), "hours": 10.0, "description": "Montaj schelă etaj 4-7 fațadă nord"},
            {"task_id": task_ids_bloc[1], "work_date": past(46), "hours": 10.0, "description": "Montaj schelă etaj 8-10 + plase protecție"},
            {"task_id": task_ids_bloc[2], "work_date": past(39), "hours": 8.0, "description": "Curățare fațadă nord — hidrosablare"},
            {"task_id": task_ids_bloc[2], "work_date": past(38), "hours": 8.0, "description": "Grunduire fațadă nord completă"},
            {"task_id": task_ids_bloc[3], "work_date": past(33), "hours": 10.0, "description": "Lipire EPS zona parter + etaj 1"},
            {"task_id": task_ids_bloc[3], "work_date": past(30), "hours": 10.0, "description": "Lipire EPS etaj 2-4"},
            {"task_id": task_ids_bloc[3], "work_date": past(27), "hours": 10.0, "description": "Lipire EPS etaj 5-7"},
            {"task_id": task_ids_bloc[3], "work_date": past(24), "hours": 10.0, "description": "Lipire EPS etaj 8-10 + armare plasă"},
            {"task_id": task_ids_bloc[4], "work_date": past(18), "hours": 10.0, "description": "Lipire EPS fațadă est — parter-etaj 3"},
            {"task_id": task_ids_bloc[4], "work_date": past(15), "hours": 10.0, "description": "Lipire EPS fațadă est — etaj 4-7"},
            {"task_id": task_ids_bloc[6], "work_date": past(12), "hours": 8.0, "description": "Demontare ferestre vechi etaj 1-2"},
            {"task_id": task_ids_bloc[6], "work_date": past(10), "hours": 8.0, "description": "Montaj ferestre PVC etaj 1-2"},
        ]
        for ts in timesheets:
            if ts["task_id"]:
                api("POST", f"/api/v1/pm/projects/{project_ids[0]}/timesheets", ts)
        print(f"    Timesheets: {len(timesheets)} entries logged")

    # ── Energy Impact — all 3 projects ───────────────────────────────────────

    energy_impacts = [
        {
            "project_id": project_ids[0],
            "property_id": prop_ids[0],
            "pre_kwh_annual": 864000.0,
            "pre_co2_kg_annual": 172800.0,
            "pre_u_value_avg": 1.8,
            "post_kwh_annual": 312000.0,
            "post_co2_kg_annual": 62400.0,
            "post_u_value_avg": 0.45,
            "estimated_kwh_savings": 552000.0,
            "estimated_co2_reduction": 110400.0,
            "total_area_sqm": 4800.0,
            "treated_area_sqm": 3280.0,
            "total_project_cost": 485000.0,
            "duration_days": 175,
            "materials_summary": {"eps_15cm_mp": 2800, "vata_minerala_mp": 480, "ferestre_pvc_buc": 120, "tencuiala_siliconica_mp": 2800},
        },
        {
            "project_id": project_ids[1],
            "property_id": prop_ids[1],
            "pre_kwh_annual": 396000.0,
            "pre_co2_kg_annual": 79200.0,
            "pre_u_value_avg": 2.2,
            "estimated_kwh_savings": 237600.0,
            "estimated_co2_reduction": 47520.0,
            "total_area_sqm": 2200.0,
            "treated_area_sqm": 2150.0,
            "total_project_cost": 320000.0,
            "duration_days": 180,
        },
        {
            "project_id": project_ids[2],
            "property_id": prop_ids[2],
            "pre_kwh_annual": 18200.0,
            "pre_co2_kg_annual": 3640.0,
            "pre_u_value_avg": 1.2,
            "post_kwh_annual": 7280.0,
            "post_co2_kg_annual": 1456.0,
            "post_u_value_avg": 0.38,
            "estimated_kwh_savings": 10920.0,
            "estimated_co2_reduction": 2184.0,
            "actual_kwh_savings": 11200.0,
            "actual_co2_reduction": 2240.0,
            "total_area_sqm": 280.0,
            "treated_area_sqm": 320.0,
            "total_project_cost": 67000.0,
            "duration_days": 120,
            "materials_summary": {"eps_10cm_mp": 320, "ferestre_pvc_buc": 12, "tencuiala_mp": 320},
        },
    ]

    for ei in energy_impacts:
        pid = ei.pop("project_id")
        if pid:
            result = api("PUT", f"/api/v1/pm/projects/{pid}/energy-impact", ei)
            if result:
                print(f"    Energy Impact: PRE {ei.get('pre_kwh_annual', '?')} → POST {ei.get('post_kwh_annual', 'TBD')} kWh/an")

    # ── Daily Reports for Project 1 ──────────────────────────────────────────

    if project_ids[0]:
        daily_reports = [
            {"report_date": past(50), "weather": "Însorit, 18°C", "temperature_min": 12.0, "temperature_max": 18.0, "activities_summary": "Montaj schelă fațadă nord etaj 1-3. Livrare plăci EPS.", "personnel_present": {"muncitori": 8, "inginer_șantier": 1}, "equipment_used": {"macara": 1, "schelă_secțiuni": 12}},
            {"report_date": past(35), "weather": "Parțial noros, 22°C", "temperature_min": 16.0, "temperature_max": 22.0, "activities_summary": "Lipire plăci EPS 15cm pe fațadă nord parter+etaj1. Consum 180mp EPS.", "personnel_present": {"izolatori": 6, "muncitori": 4, "inginer_șantier": 1}, "equipment_used": {"lift_materiale": 1}, "observations": "Calitate lipire bună, aderență verificată"},
            {"report_date": past(15), "weather": "Ploaie ușoară, 14°C", "temperature_min": 10.0, "temperature_max": 14.0, "activities_summary": "Lipire EPS fațadă est etaj 4-7. Oprire la 13:00 din cauza ploii.", "personnel_present": {"izolatori": 6, "muncitori": 3}, "issues": "Oprire lucrări de izolare la 13:00 — umiditate peste limită. Continuare a doua zi."},
        ]
        for dr in daily_reports:
            api("POST", f"/api/v1/pm/projects/{project_ids[0]}/daily-reports", dr)
        print(f"    Daily Reports: {len(daily_reports)} entries")

    return {"project_ids": project_ids}


def update_project_progress():
    """Set percent_complete and status on each project."""
    print("\n── update_project_progress ──")
    progress_map = {
        "Reabilitare termică Bloc A4 Iași": {"percent_complete": 44.0, "status": "in_progress"},
        "Izolare termică Școala Nr. 5 Bacău": {"percent_complete": 0.0, "status": "planning"},
        "Renovare energetică Vila Popescu": {"percent_complete": 100.0, "status": "completed"},
    }
    projects = api("GET", "/api/v1/pm/projects?per_page=50")
    if not projects:
        print("    No projects found")
        return
    for p in projects:
        update = progress_map.get(p.get("name", ""))
        if update:
            api("PUT", f"/api/v1/pm/projects/{p['id']}", update)
            print(f"    {p['name']} → {update['percent_complete']}% ({update['status']})")


# ═════════════════════════════════════════════════════════════════════════════
# RM — 8 Employees, 5 Equipment, Materials, Allocations (P2+P3)
# (F107-F121)
# ═════════════════════════════════════════════════════════════════════════════


def seed_rm(pm_data):
    print("\n═══ RM ═══")
    project_ids = pm_data["project_ids"]

    now = datetime.utcnow()
    d = lambda days: (now + timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S")
    past = lambda days: (now - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S")

    # ── 8 Employees ──────────────────────────────────────────────────────────

    employees_data = [
        {"first_name": "Marian", "last_name": "Ciobanu", "email": "marian.ciobanu@bahm.ro", "phone": "0745110110", "employee_number": "EMP-001", "position": "Șef Șantier", "department": "Execuție", "cost_center": "CC-EXEC", "contract_type": "full_time", "hire_date": past(1200), "gross_salary": 8500.0, "net_salary": 5100.0, "hourly_rate": 50.6, "skills": ["management șantier", "citire planuri", "coordonare echipe"], "qualifications": ["Inginer construcții civile"], "certifications": ["Responsabil tehnic execuție (RTE)", "SSM nivel mediu"]},
        {"first_name": "Gheorghe", "last_name": "Lupu", "email": "gheorghe.lupu@bahm.ro", "phone": "0745220220", "employee_number": "EMP-002", "position": "Izolator Termic Senior", "department": "Execuție", "cost_center": "CC-EXEC", "contract_type": "full_time", "hire_date": past(900), "gross_salary": 6200.0, "net_salary": 3720.0, "hourly_rate": 36.9, "skills": ["montaj EPS", "montaj vată minerală", "tencuieli decorative", "hidroizolații"], "qualifications": ["Calificare izolator termic"], "certifications": ["Lucru la înălțime"]},
        {"first_name": "Vasile", "last_name": "Rotaru", "email": "vasile.rotaru@bahm.ro", "phone": "0745330330", "employee_number": "EMP-003", "position": "Tâmplar PVC/Aluminiu", "department": "Execuție", "cost_center": "CC-EXEC", "contract_type": "full_time", "hire_date": past(700), "gross_salary": 5800.0, "net_salary": 3480.0, "hourly_rate": 34.5, "skills": ["montaj ferestre PVC", "montaj uși", "reglaje tâmplărie", "etanșare"], "qualifications": ["Tâmplar aluminium și PVC"]},
        {"first_name": "Ion", "last_name": "Cazacu", "email": "ion.cazacu@bahm.ro", "phone": "0745440440", "employee_number": "EMP-004", "position": "Instalator HVAC", "department": "Instalații", "cost_center": "CC-INST", "contract_type": "full_time", "hire_date": past(500), "gross_salary": 7000.0, "net_salary": 4200.0, "hourly_rate": 41.7, "skills": ["instalare centrale termice", "montaj radiatoare", "țevi cupru/PPR", "automatizări"], "qualifications": ["Instalator sanitar și termic autorizat ISCIR"], "certifications": ["Autorizare ANRE", "Sudură PPR"]},
        {"first_name": "Petru", "last_name": "Sandu", "email": "petru.sandu@bahm.ro", "phone": "0745550550", "employee_number": "EMP-005", "position": "Zugrav-Finiseur", "department": "Execuție", "cost_center": "CC-EXEC", "contract_type": "full_time", "hire_date": past(400), "gross_salary": 5200.0, "net_salary": 3120.0, "hourly_rate": 31.0, "skills": ["tencuieli mecanizate", "finisaje decorative", "vopsitorii", "gleturi"]},
        {"first_name": "Alexandru", "last_name": "Mircea", "email": "alex.mircea@bahm.ro", "phone": "0745660660", "employee_number": "EMP-006", "position": "Inginer Energetician", "department": "Proiectare", "cost_center": "CC-PROJ", "contract_type": "full_time", "hire_date": past(600), "gross_salary": 9000.0, "net_salary": 5400.0, "hourly_rate": 53.6, "skills": ["audit energetic", "certificare energetică", "calcul coeficient U", "simulări termice"], "qualifications": ["Inginer instalații", "Auditor energetic gradul I"], "certifications": ["Auditor energetic MDLPA", "Certificator energetic"]},
        {"first_name": "Cosmin", "last_name": "Diaconu", "email": "cosmin.diaconu@bahm.ro", "phone": "0745770770", "employee_number": "EMP-007", "position": "Muncitor Necalificat", "department": "Execuție", "cost_center": "CC-EXEC", "contract_type": "full_time", "hire_date": past(200), "gross_salary": 4200.0, "net_salary": 2520.0, "hourly_rate": 25.0, "skills": ["transport materiale", "curățenie șantier", "ajutor montaj"]},
        {"first_name": "Dragoș", "last_name": "Enache", "email": "dragos.enache@extern.ro", "phone": "0745880880", "employee_number": "EXT-001", "position": "Consultant Structural", "department": "Extern", "cost_center": "CC-EXT", "contract_type": "contract", "hire_date": past(100), "hourly_rate": 75.0, "is_external": True, "external_company": "StructPro Engineering SRL", "external_contract_ref": "CTR-EXT-2025-01", "external_daily_rate": 600.0, "skills": ["analiză structurală", "expertize tehnice", "consolidări"], "qualifications": ["Inginer structurist"], "certifications": ["Expert tehnic atestat MDLPA"]},
    ]

    emp_ids = []
    for e in employees_data:
        result = api("POST", "/api/v1/rm/employees", e)
        if result:
            eid = result.get("id", "?")
            emp_ids.append(eid)
            ext = " [EXTERN]" if e.get("is_external") else ""
            print(f"  Employee: {e['first_name']} {e['last_name']} — {e['position']}{ext} → {eid}")
        else:
            emp_ids.append(None)

    # ── 5 Equipment ──────────────────────────────────────────────────────────

    equipment_data = [
        {"name": "Schelă metalică tubulară 200mp", "code": "EQ-SCH-01", "category": "Acces înălțime", "description": "Schelă tubulară certificată H=30m, S=200mp fațadă", "manufacturer": "Layher", "model": "Allround TG60", "serial_number": "LAY-2021-4455", "purchase_date": past(800), "purchase_cost": 42000.0, "daily_rate": 120.0, "location": "Depozit CUG Iași"},
        {"name": "Betonieră 250L", "code": "EQ-BET-01", "category": "Preparare", "description": "Betonieră electrică 250 litri, 230V", "manufacturer": "Imer", "model": "Syntesi 250", "serial_number": "IMR-2022-1122", "purchase_date": past(600), "purchase_cost": 4500.0, "daily_rate": 45.0, "location": "Depozit CUG Iași"},
        {"name": "Lift materiale 200kg", "code": "EQ-LFT-01", "category": "Transport vertical", "description": "Lift electric materiale, capacitate 200kg, H max 30m", "manufacturer": "Geda", "model": "200Z", "serial_number": "GDA-2023-7788", "purchase_date": past(400), "purchase_cost": 18000.0, "daily_rate": 85.0, "location": "Șantier Bloc A4 Iași"},
        {"name": "Mașină tencuit mecanizat", "code": "EQ-TNC-01", "category": "Finisaje", "description": "Stație tencuit mecanizat, debit 25L/min", "manufacturer": "PFT", "model": "G4", "serial_number": "PFT-2020-3344", "purchase_date": past(1000), "purchase_cost": 28000.0, "daily_rate": 150.0, "location": "Depozit CUG Iași"},
        {"name": "Autoplatformă 12m", "code": "EQ-APL-01", "category": "Acces înălțime", "description": "Autoplatformă articulată, H max 12m, 230kg", "manufacturer": "Haulotte", "model": "Star 12", "serial_number": "HLT-2019-9900", "purchase_date": past(1500), "purchase_cost": 85000.0, "daily_rate": 250.0, "location": "Depozit CUG Iași"},
    ]

    equip_ids = []
    for eq in equipment_data:
        result = api("POST", "/api/v1/rm/equipment", eq)
        if result:
            eqid = result.get("id", "?")
            equip_ids.append(eqid)
            print(f"  Equipment: {eq['name']} → {eqid}")
        else:
            equip_ids.append(None)

    # ── Material Stocks ──────────────────────────────────────────────────────

    materials_data = [
        {"name": "Polistiren expandat EPS 80 — 15cm", "code": "STK-EPS15", "unit_of_measure": "mp", "current_quantity": 1200.0, "minimum_quantity": 200.0, "location": "Depozit CUG", "warehouse": "Hala A", "unit_cost": 52.0},
        {"name": "Polistiren expandat EPS 80 — 10cm", "code": "STK-EPS10", "unit_of_measure": "mp", "current_quantity": 450.0, "minimum_quantity": 100.0, "location": "Depozit CUG", "warehouse": "Hala A", "unit_cost": 38.0},
        {"name": "Vată minerală bazaltică 15cm", "code": "STK-VMB15", "unit_of_measure": "mp", "current_quantity": 600.0, "minimum_quantity": 100.0, "location": "Depozit CUG", "warehouse": "Hala A", "unit_cost": 72.0},
        {"name": "Adeziv polistiren — saci 25kg", "code": "STK-ADZ25", "unit_of_measure": "buc", "current_quantity": 180.0, "minimum_quantity": 50.0, "location": "Depozit CUG", "warehouse": "Hala B", "unit_cost": 42.0},
        {"name": "Plasă armătură fibră 160g/mp", "code": "STK-PLA160", "unit_of_measure": "mp", "current_quantity": 2000.0, "minimum_quantity": 300.0, "location": "Depozit CUG", "warehouse": "Hala A", "unit_cost": 8.5},
        {"name": "Tencuială decorativă siliconică 25kg", "code": "STK-TDS25", "unit_of_measure": "buc", "current_quantity": 85.0, "minimum_quantity": 20.0, "location": "Depozit CUG", "warehouse": "Hala B", "unit_cost": 185.0},
        {"name": "Dibluri termoizolație 10x160mm", "code": "STK-DIB160", "unit_of_measure": "buc", "current_quantity": 5000.0, "minimum_quantity": 1000.0, "location": "Depozit CUG", "warehouse": "Hala C", "unit_cost": 1.2},
        {"name": "Profil PVC fereastră 5 camere — 6m", "code": "STK-PVC5C", "unit_of_measure": "buc", "current_quantity": 60.0, "minimum_quantity": 10.0, "location": "Depozit CUG", "warehouse": "Hala D", "unit_cost": 145.0},
        {"name": "Geam termoizolant tripan 4-16-4-16-4", "code": "STK-GT3", "unit_of_measure": "mp", "current_quantity": 120.0, "minimum_quantity": 20.0, "location": "Depozit CUG", "warehouse": "Hala D", "unit_cost": 210.0},
        {"name": "Spumă poliuretanică montaj — 750ml", "code": "STK-SPM750", "unit_of_measure": "buc", "current_quantity": 200.0, "minimum_quantity": 50.0, "location": "Depozit CUG", "warehouse": "Hala C", "unit_cost": 18.0},
    ]

    mat_ids = []
    for m in materials_data:
        result = api("POST", "/api/v1/rm/materials", m)
        if result:
            mid = result.get("id", "?")
            mat_ids.append(mid)
            print(f"  Material: {m['name'][:45]}... qty={m['current_quantity']}")
        else:
            mat_ids.append(None)

    # ── Resource Allocations on Projects ─────────────────────────────────────

    allocations_data = []

    # Project 1 — Bloc A4 (in execution): 5 employees + 2 equipment
    if project_ids[0]:
        allocations_data += [
            {"resource_type": "employee", "employee_id": emp_ids[0], "project_id": project_ids[0], "start_date": past(55), "end_date": d(120), "allocated_hours": 800.0, "planned_cost": 40480.0, "allocation_percent": 100.0},
            {"resource_type": "employee", "employee_id": emp_ids[1], "project_id": project_ids[0], "start_date": past(50), "end_date": d(60), "allocated_hours": 600.0, "planned_cost": 22140.0, "allocation_percent": 100.0},
            {"resource_type": "employee", "employee_id": emp_ids[2], "project_id": project_ids[0], "start_date": past(15), "end_date": d(30), "allocated_hours": 320.0, "planned_cost": 11040.0, "allocation_percent": 100.0},
            {"resource_type": "employee", "employee_id": emp_ids[4], "project_id": project_ids[0], "start_date": d(5), "end_date": d(50), "allocated_hours": 280.0, "planned_cost": 8680.0, "allocation_percent": 80.0},
            {"resource_type": "employee", "employee_id": emp_ids[6], "project_id": project_ids[0], "start_date": past(55), "end_date": d(60), "allocated_hours": 500.0, "planned_cost": 12500.0, "allocation_percent": 100.0},
            {"resource_type": "equipment", "equipment_id": equip_ids[0], "project_id": project_ids[0], "start_date": past(50), "end_date": d(30), "planned_cost": 9600.0},
            {"resource_type": "equipment", "equipment_id": equip_ids[2], "project_id": project_ids[0], "start_date": past(40), "end_date": d(60), "planned_cost": 8500.0},
        ]

    # Project 2 — Școala Bacău (planning): 2 employees planned
    if project_ids[1]:
        allocations_data += [
            {"resource_type": "employee", "employee_id": emp_ids[5], "project_id": project_ids[1], "start_date": d(30), "end_date": d(60), "allocated_hours": 120.0, "planned_cost": 6432.0, "allocation_percent": 50.0},
            {"resource_type": "employee", "employee_id": emp_ids[7], "project_id": project_ids[1], "start_date": d(35), "end_date": d(50), "allocated_hours": 60.0, "planned_cost": 4500.0, "allocation_percent": 30.0},
        ]

    # Project 3 — Vila Popescu (completed): 2 employees historical
    if project_ids[2]:
        allocations_data += [
            {"resource_type": "employee", "employee_id": emp_ids[1], "project_id": project_ids[2], "start_date": past(140), "end_date": past(60), "allocated_hours": 160.0, "planned_cost": 5904.0, "allocation_percent": 50.0},
            {"resource_type": "employee", "employee_id": emp_ids[2], "project_id": project_ids[2], "start_date": past(100), "end_date": past(80), "allocated_hours": 48.0, "planned_cost": 1656.0, "allocation_percent": 100.0},
        ]

    alloc_ids = []
    for a in allocations_data:
        clean = {k: v for k, v in a.items() if v is not None}
        result = api("POST", "/api/v1/rm/allocations", clean)
        if result:
            alloc_ids.append(result.get("id"))
            rtype = a["resource_type"]
            print(f"    Allocation [{rtype}]: project {str(a['project_id'])[:8]}...")
        else:
            alloc_ids.append(None)

    return {
        "emp_ids": emp_ids,
        "equip_ids": equip_ids,
        "mat_ids": mat_ids,
        "alloc_ids": alloc_ids,
    }


# ═════════════════════════════════════════════════════════════════════════════
# 5. BI — KPI definitions, dashboards, reports (P3)
# ═════════════════════════════════════════════════════════════════════════════

def seed_bi(pm_data):
    """F132, F133, F135, F148, F152 — KPIs, dashboards, reports."""
    print("\n── seed_bi ──")
    project_ids = pm_data.get("project_ids", [])

    # ── 8 KPI definitions ──────────────────────────────────────────────────
    kpis = [
        {
            "name": "Rata conversie oportunități",
            "code": "KPI_CONV_RATE",
            "description": "Procentul de oportunități câștigate din totalul închise",
            "module": "pipeline",
            "formula": {"type": "ratio", "numerator": "opportunities_won", "denominator": "opportunities_closed"},
            "formula_text": "won / (won + lost) * 100",
            "unit": "%",
            "display_type": "gauge",
            "thresholds": [{"color": "red", "min": 0, "max": 30}, {"color": "yellow", "min": 30, "max": 60}, {"color": "green", "min": 60, "max": 100}],
            "assigned_roles": ["admin", "manager_vanzari"],
            "sort_order": 1,
        },
        {
            "name": "Valoare medie contract",
            "code": "KPI_AVG_CONTRACT",
            "description": "Valoarea medie a contractelor semnate",
            "module": "pipeline",
            "formula": {"type": "average", "field": "contract_value", "source": "contracts_signed"},
            "formula_text": "SUM(contract_value) / COUNT(contracts)",
            "unit": "RON",
            "display_type": "number",
            "thresholds": [{"color": "red", "min": 0, "max": 50000}, {"color": "yellow", "min": 50000, "max": 150000}, {"color": "green", "min": 150000, "max": 999999}],
            "assigned_roles": ["admin", "manager_vanzari"],
            "sort_order": 2,
        },
        {
            "name": "CPI — Cost Performance Index",
            "code": "KPI_CPI",
            "description": "Earned Value / Actual Cost — eficiență costuri proiect",
            "module": "pm",
            "formula": {"type": "evm", "metric": "CPI", "numerator": "earned_value", "denominator": "actual_cost"},
            "formula_text": "EV / AC",
            "unit": "",
            "display_type": "gauge",
            "thresholds": [{"color": "red", "min": 0, "max": 0.9}, {"color": "yellow", "min": 0.9, "max": 1.0}, {"color": "green", "min": 1.0, "max": 2.0}],
            "assigned_roles": ["admin", "manager_vanzari", "tehnician"],
            "sort_order": 3,
        },
        {
            "name": "SPI — Schedule Performance Index",
            "code": "KPI_SPI",
            "description": "Earned Value / Planned Value — eficiență program",
            "module": "pm",
            "formula": {"type": "evm", "metric": "SPI", "numerator": "earned_value", "denominator": "planned_value"},
            "formula_text": "EV / PV",
            "unit": "",
            "display_type": "gauge",
            "thresholds": [{"color": "red", "min": 0, "max": 0.9}, {"color": "yellow", "min": 0.9, "max": 1.0}, {"color": "green", "min": 1.0, "max": 2.0}],
            "assigned_roles": ["admin", "tehnician"],
            "sort_order": 4,
        },
        {
            "name": "Economie energetică totală",
            "code": "KPI_ENERGY_SAVE",
            "description": "Total kWh/an economisiți prin reabilitări finalizate",
            "module": "pm",
            "formula": {"type": "sum", "field": "actual_kwh_savings", "source": "energy_impacts_completed"},
            "formula_text": "SUM(pre_kwh - post_kwh) WHERE status=completed",
            "unit": "kWh/an",
            "display_type": "number",
            "thresholds": [{"color": "yellow", "min": 0, "max": 100000}, {"color": "green", "min": 100000, "max": 9999999}],
            "assigned_roles": ["admin"],
            "sort_order": 5,
        },
        {
            "name": "Reducere emisii CO₂",
            "code": "KPI_CO2_REDUCE",
            "description": "Tone CO₂/an reduse prin proiecte finalizate",
            "module": "pm",
            "formula": {"type": "sum", "field": "co2_reduction_tons", "source": "energy_impacts_completed"},
            "formula_text": "SUM(co2_reduction_tons)",
            "unit": "t CO₂/an",
            "display_type": "number",
            "thresholds": [{"color": "yellow", "min": 0, "max": 50}, {"color": "green", "min": 50, "max": 99999}],
            "assigned_roles": ["admin"],
            "sort_order": 6,
        },
        {
            "name": "Utilizare resurse umane",
            "code": "KPI_HR_UTIL",
            "description": "Procentul mediu de alocare a angajaților activi",
            "module": "rm",
            "formula": {"type": "average", "field": "allocation_percent", "source": "active_allocations_employee"},
            "formula_text": "AVG(allocation_percent) WHERE resource_type=employee",
            "unit": "%",
            "display_type": "gauge",
            "thresholds": [{"color": "red", "min": 0, "max": 50}, {"color": "yellow", "min": 50, "max": 80}, {"color": "green", "min": 80, "max": 100}],
            "assigned_roles": ["admin"],
            "sort_order": 7,
        },
        {
            "name": "Nr. contacte noi / lună",
            "code": "KPI_NEW_CONTACTS",
            "description": "Contacte CRM create în ultima lună",
            "module": "crm",
            "formula": {"type": "count", "source": "contacts", "period": "month"},
            "formula_text": "COUNT(contacts WHERE created_at > NOW()-30d)",
            "unit": "",
            "display_type": "number",
            "thresholds": [{"color": "red", "min": 0, "max": 5}, {"color": "yellow", "min": 5, "max": 15}, {"color": "green", "min": 15, "max": 999}],
            "assigned_roles": ["admin", "manager_vanzari", "agent_comercial"],
            "sort_order": 8,
        },
    ]

    kpi_ids = []
    for k in kpis:
        result = api("POST", "/api/v1/bi/kpis", k)
        if result:
            kpi_ids.append(result["id"])
            print(f"    KPI: {k['code']} — {k['name']}")
        else:
            kpi_ids.append(None)

    # ── KPI values (sample measurements) ───────────────────────────────────
    from datetime import datetime, timedelta
    now = datetime.utcnow()
    kpi_values = [
        {"kpi_definition_id": kpi_ids[0], "value": 66.7, "threshold_color": "green", "period_start": (now - timedelta(days=30)).isoformat(), "period_end": now.isoformat()},
        {"kpi_definition_id": kpi_ids[1], "value": 187500.0, "threshold_color": "green", "period_start": (now - timedelta(days=30)).isoformat(), "period_end": now.isoformat()},
        {"kpi_definition_id": kpi_ids[2], "value": 1.05, "threshold_color": "green", "period_start": (now - timedelta(days=7)).isoformat(), "period_end": now.isoformat()},
        {"kpi_definition_id": kpi_ids[3], "value": 0.92, "threshold_color": "yellow", "period_start": (now - timedelta(days=7)).isoformat(), "period_end": now.isoformat()},
        {"kpi_definition_id": kpi_ids[4], "value": 595200.0, "threshold_color": "green", "period_start": (now - timedelta(days=90)).isoformat(), "period_end": now.isoformat()},
        {"kpi_definition_id": kpi_ids[5], "value": 142.8, "threshold_color": "green", "period_start": (now - timedelta(days=90)).isoformat(), "period_end": now.isoformat()},
        {"kpi_definition_id": kpi_ids[6], "value": 75.0, "threshold_color": "yellow", "period_start": (now - timedelta(days=7)).isoformat(), "period_end": now.isoformat()},
        {"kpi_definition_id": kpi_ids[7], "value": 15.0, "threshold_color": "green", "period_start": (now - timedelta(days=30)).isoformat(), "period_end": now.isoformat()},
    ]

    # Add project_id for project-level KPIs
    if project_ids and project_ids[0]:
        kpi_values[2]["project_id"] = project_ids[0]
        kpi_values[3]["project_id"] = project_ids[0]

    val_count = 0
    for v in kpi_values:
        if v["kpi_definition_id"] is None:
            continue
        kid = v["kpi_definition_id"]
        result = api("POST", f"/api/v1/bi/kpis/{kid}/values", v)
        if result:
            val_count += 1

    print(f"    KPI values recorded: {val_count}")

    # ── 3 Dashboards with widgets ──────────────────────────────────────────
    dashboards = [
        {
            "name": "Executive Overview",
            "description": "Dashboard executiv — KPIs cross-module, pipeline, energie",
            "dashboard_type": "executive",
            "is_default": True,
            "layout_config": {"columns": 4, "row_height": 120},
            "visible_roles": ["admin", "manager_vanzari"],
            "widgets": [
                {"widget_type": "kpi_card", "title": "Rata Conversie", "config": {"color": "blue"}, "data_source": {"kpi_code": "KPI_CONV_RATE"}, "position_x": 0, "position_y": 0, "width": 1, "height": 1, "sort_order": 1, "kpi_definition_id": kpi_ids[0] if kpi_ids[0] else None},
                {"widget_type": "kpi_card", "title": "Val. Medie Contract", "config": {"color": "green", "format": "currency"}, "data_source": {"kpi_code": "KPI_AVG_CONTRACT"}, "position_x": 1, "position_y": 0, "width": 1, "height": 1, "sort_order": 2, "kpi_definition_id": kpi_ids[1] if kpi_ids[1] else None},
                {"widget_type": "kpi_card", "title": "Economie Energetică", "config": {"color": "orange"}, "data_source": {"kpi_code": "KPI_ENERGY_SAVE"}, "position_x": 2, "position_y": 0, "width": 1, "height": 1, "sort_order": 3, "kpi_definition_id": kpi_ids[4] if kpi_ids[4] else None},
                {"widget_type": "kpi_card", "title": "Contacte Noi", "config": {"color": "purple"}, "data_source": {"kpi_code": "KPI_NEW_CONTACTS"}, "position_x": 3, "position_y": 0, "width": 1, "height": 1, "sort_order": 4, "kpi_definition_id": kpi_ids[7] if kpi_ids[7] else None},
                {"widget_type": "chart", "title": "Pipeline per Etapă", "config": {"chart_type": "bar", "colors": ["#1890ff", "#52c41a", "#faad14", "#f5222d"]}, "data_source": {"type": "pipeline_by_stage"}, "position_x": 0, "position_y": 1, "width": 2, "height": 2, "sort_order": 5},
                {"widget_type": "chart", "title": "Proiecte — CPI vs SPI", "config": {"chart_type": "scatter", "x_axis": "CPI", "y_axis": "SPI"}, "data_source": {"type": "projects_evm"}, "position_x": 2, "position_y": 1, "width": 2, "height": 2, "sort_order": 6},
            ],
        },
        {
            "name": "Energie & Sustenabilitate",
            "description": "Dashboard P1 — indicatori energetici, CO₂, clase energetice",
            "dashboard_type": "energy",
            "is_default": False,
            "layout_config": {"columns": 3, "row_height": 140},
            "visible_roles": ["admin", "tehnician"],
            "widgets": [
                {"widget_type": "kpi_card", "title": "kWh Economisiți", "config": {"color": "green", "icon": "thunderbolt"}, "data_source": {"kpi_code": "KPI_ENERGY_SAVE"}, "position_x": 0, "position_y": 0, "width": 1, "height": 1, "sort_order": 1, "kpi_definition_id": kpi_ids[4] if kpi_ids[4] else None},
                {"widget_type": "kpi_card", "title": "CO₂ Redus", "config": {"color": "cyan", "icon": "cloud"}, "data_source": {"kpi_code": "KPI_CO2_REDUCE"}, "position_x": 1, "position_y": 0, "width": 1, "height": 1, "sort_order": 2, "kpi_definition_id": kpi_ids[5] if kpi_ids[5] else None},
                {"widget_type": "kpi_card", "title": "CPI Proiect", "config": {"color": "blue"}, "data_source": {"kpi_code": "KPI_CPI"}, "position_x": 2, "position_y": 0, "width": 1, "height": 1, "sort_order": 3, "kpi_definition_id": kpi_ids[2] if kpi_ids[2] else None},
                {"widget_type": "chart", "title": "Consum PRE vs POST (kWh/an)", "config": {"chart_type": "grouped_bar", "series": ["pre_kwh", "post_kwh"]}, "data_source": {"type": "energy_impact_comparison"}, "position_x": 0, "position_y": 1, "width": 2, "height": 2, "sort_order": 4},
                {"widget_type": "table", "title": "Proiecte — Impact Energetic", "config": {"columns": ["project", "pre_kwh", "post_kwh", "savings_pct", "co2_tons"]}, "data_source": {"type": "energy_impact_list"}, "position_x": 2, "position_y": 1, "width": 1, "height": 2, "sort_order": 5},
            ],
        },
        {
            "name": "Resurse & Operațional",
            "description": "Dashboard P2 — utilizare personal, echipamente, stocuri",
            "dashboard_type": "operational",
            "is_default": False,
            "layout_config": {"columns": 3, "row_height": 130},
            "visible_roles": ["admin"],
            "widgets": [
                {"widget_type": "kpi_card", "title": "Utilizare HR", "config": {"color": "violet"}, "data_source": {"kpi_code": "KPI_HR_UTIL"}, "position_x": 0, "position_y": 0, "width": 1, "height": 1, "sort_order": 1, "kpi_definition_id": kpi_ids[6] if kpi_ids[6] else None},
                {"widget_type": "kpi_card", "title": "SPI Proiect", "config": {"color": "gold"}, "data_source": {"kpi_code": "KPI_SPI"}, "position_x": 1, "position_y": 0, "width": 1, "height": 1, "sort_order": 2, "kpi_definition_id": kpi_ids[3] if kpi_ids[3] else None},
                {"widget_type": "chart", "title": "Alocare pe Proiecte", "config": {"chart_type": "stacked_bar"}, "data_source": {"type": "allocations_by_project"}, "position_x": 0, "position_y": 1, "width": 2, "height": 2, "sort_order": 3},
                {"widget_type": "table", "title": "Stocuri Critice", "config": {"columns": ["material", "quantity", "min_stock", "status"]}, "data_source": {"type": "material_stocks_low"}, "position_x": 2, "position_y": 0, "width": 1, "height": 3, "sort_order": 4},
            ],
        },
    ]

    dash_ids = []
    for d in dashboards:
        widgets = d.pop("widgets", [])
        clean_widgets = []
        for w in widgets:
            cw = {k: v for k, v in w.items() if v is not None}
            clean_widgets.append(cw)
        d["widgets"] = clean_widgets
        result = api("POST", "/api/v1/bi/dashboards", d)
        if result:
            dash_ids.append(result["id"])
            wcount = len(result.get("widgets", []))
            print(f"    Dashboard: {result['name']} ({wcount} widgets)")
        else:
            dash_ids.append(None)

    # ── 4 Report definitions ───────────────────────────────────────────────
    reports = [
        {
            "name": "Raport Pipeline Lunar",
            "description": "Oportunități create, câștigate, pierdute + valoare pipeline",
            "report_type": "scheduled",
            "module": "pipeline",
            "query_config": {"source": "opportunities", "period": "month", "group_by": "stage"},
            "columns_config": [{"field": "stage", "label": "Etapă"}, {"field": "count", "label": "Nr."}, {"field": "total_value", "label": "Valoare (RON)"}],
            "filters_config": [{"field": "created_at", "operator": "last_n_days", "value": 30}],
            "chart_config": {"type": "funnel", "value_field": "total_value"},
            "is_scheduled": True,
            "schedule_cron": "0 8 1 * *",
            "recipients": ["admin", "manager_vanzari"],
        },
        {
            "name": "Raport Eficiență Energetică",
            "description": "Sinteză economii kWh și CO₂ pe proiecte finalizate",
            "report_type": "custom",
            "module": "pm",
            "query_config": {"source": "energy_impacts", "filter": {"status": "completed"}},
            "columns_config": [{"field": "project_name", "label": "Proiect"}, {"field": "pre_kwh", "label": "Pre (kWh)"}, {"field": "post_kwh", "label": "Post (kWh)"}, {"field": "savings_pct", "label": "Economie %"}, {"field": "co2_tons", "label": "CO₂ (t)"}],
            "grouping_config": {"group_by": "energy_class_after"},
        },
        {
            "name": "Raport Utilizare Resurse",
            "description": "Grad de ocupare angajați și echipamente pe proiecte",
            "report_type": "custom",
            "module": "rm",
            "query_config": {"source": "resource_allocations", "group_by": "resource_type"},
            "columns_config": [{"field": "resource_name", "label": "Resursă"}, {"field": "project_name", "label": "Proiect"}, {"field": "allocation_percent", "label": "Alocare %"}, {"field": "planned_cost", "label": "Cost Planificat"}],
            "filters_config": [{"field": "end_date", "operator": "gte", "value": "today"}],
        },
        {
            "name": "Raport Contacte și Conversii",
            "description": "Contacte noi, rata de conversie lead→opportunity, top clienți",
            "report_type": "scheduled",
            "module": "crm",
            "query_config": {"source": "contacts", "join": "opportunities", "period": "quarter"},
            "columns_config": [{"field": "contact_name", "label": "Contact"}, {"field": "type", "label": "Tip"}, {"field": "opp_count", "label": "Oportunități"}, {"field": "total_value", "label": "Valoare Totală"}],
            "chart_config": {"type": "pie", "value_field": "total_value", "label_field": "type"},
            "is_scheduled": True,
            "schedule_cron": "0 9 1 1,4,7,10 *",
            "recipients": ["admin", "manager_vanzari", "agent_comercial"],
        },
    ]

    report_ids = []
    for r in reports:
        result = api("POST", "/api/v1/bi/reports", r)
        if result:
            report_ids.append(result["id"])
            print(f"    Report: {r['name']}")
        else:
            report_ids.append(None)

    return {
        "kpi_ids": kpi_ids,
        "dash_ids": dash_ids,
        "report_ids": report_ids,
    }


# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════

def already_seeded():
    """Check if seed data already exists by querying opportunities."""
    req = urllib.request.Request(
        f"{API}/api/v1/pipeline/opportunities?per_page=1",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {TOKEN}",
        },
    )
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        result = json.loads(resp.read().decode())
        total = result.get("meta", {}).get("total", 0)
        return total > 0
    except urllib.error.HTTPError:
        return False


if __name__ == "__main__":
    print("Waiting 30s for uvicorn to start...")
    sleep(30)

    login()

    if already_seeded():
        print("Date deja existente, skip seed.")
    else:
        crm = seed_crm()
        print(f"\n✓ CRM done: {len(crm['contact_ids'])} contacts, {len(crm['product_ids'])} products, {len(crm['property_ids'])} properties")
        pipe = seed_pipeline(crm)
        print(f"✓ Pipeline done: {len(pipe['opp_ids'])} opportunities, {len(pipe['offer_ids'])} offers, {len(pipe['contract_ids'])} contracts, {len(pipe['act_ids'])} activities")
        pm = seed_pm(crm, pipe)
        print(f"✓ PM done: {len(pm['project_ids'])} projects with WBS, tasks, timesheets, energy impact")
        rm = seed_rm(pm)
        print(f"✓ RM done: {len(rm['emp_ids'])} employees, {len(rm['equip_ids'])} equipment, {len(rm['mat_ids'])} materials, {len(rm['alloc_ids'])} allocations")
        bi = seed_bi(pm)
        print(f"✓ BI done: {len(bi['kpi_ids'])} KPIs, {len(bi['dash_ids'])} dashboards, {len(bi['report_ids'])} reports")

    update_project_progress()
    print("\n══ DONE ══")
