"""
BuildWise Demo Seed Data — all 3 prototypes (P1/P2/P3).
Run from Railway Console: python scripts/seed_demo_data.py
"""

import urllib.request
import json
import sys
from datetime import datetime, timedelta

API = "https://confident-cooperation-production.up.railway.app"
EMAIL = "buildwise2026x@gmail.com"
PASSWORD = "Buildwise2026"
TOKEN = None


def api(method, path, body=None):
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
# MAIN
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    login()
    ids = seed_crm()
    print(f"\n✓ CRM done: {len(ids['contact_ids'])} contacts, {len(ids['product_ids'])} products, {len(ids['property_ids'])} properties")
