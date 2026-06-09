"""
db.py — AgriMatch In-Memory Data Store
───────────────────────────────────────
All persistent state lives in st.session_state under the key "agrimatch_db".
This module exposes clean read/write helpers so every page talks to one
source of truth without importing Streamlit internals directly.

In a production deployment you would swap these helpers for SQLAlchemy
calls against a real MySQL database; the calling code in every page
would not need to change at all.
"""

import streamlit as st
from datetime import datetime, timedelta
import random

# ── Seed data ─────────────────────────────────────────────────────────────────

_SEED_LISTINGS = [
    {
        "id": 1, "farmer_id": "farmer_1",
        "farmer_name": "Kwame Asante", "phone": "+233 24 111 2233",
        "crop": "Maize", "region": "Ashanti", "city": "Kumasi",
        "qty_kg": 500, "price_per_kg": 4.50, "grade": "Grade A",
        "available_from": "2025-07-01", "notes": "Sun-dried, clean harvest.",
        "verified": True, "created_at": "2025-06-20",
    },
    {
        "id": 2, "farmer_id": "farmer_2",
        "farmer_name": "Abena Mensah", "phone": "+233 20 555 6677",
        "crop": "Tomatoes (local)", "region": "Greater Accra", "city": "Accra",
        "qty_kg": 200, "price_per_kg": 8.00, "grade": "Grade B",
        "available_from": "2025-06-28", "notes": "Fresh from greenhouse.",
        "verified": True, "created_at": "2025-06-18",
    },
    {
        "id": 3, "farmer_id": "farmer_3",
        "farmer_name": "Kofi Boateng", "phone": "+233 26 999 0011",
        "crop": "Cassava", "region": "Eastern", "city": "Koforidua",
        "qty_kg": 1000, "price_per_kg": 2.20, "grade": "Grade A",
        "available_from": "2025-07-05", "notes": "Large tubers, freshly harvested.",
        "verified": False, "created_at": "2025-06-22",
    },
    {
        "id": 4, "farmer_id": "farmer_4",
        "farmer_name": "Ama Owusu", "phone": "+233 50 333 4455",
        "crop": "Yam", "region": "Brong Ahafo", "city": "Techiman",
        "qty_kg": 750, "price_per_kg": 6.00, "grade": "Grade A",
        "available_from": "2025-07-10", "notes": "Pona variety, ideal for export.",
        "verified": True, "created_at": "2025-06-21",
    },
    {
        "id": 5, "farmer_id": "farmer_5",
        "farmer_name": "Yaw Darko", "phone": "+233 27 777 8899",
        "crop": "Rice (local)", "region": "Northern", "city": "Tamale",
        "qty_kg": 2000, "price_per_kg": 5.80, "grade": "Grade A",
        "available_from": "2025-07-15", "notes": "Polished local rice, 50kg bags.",
        "verified": True, "created_at": "2025-06-23",
    },
    {
        "id": 6, "farmer_id": "farmer_1",
        "farmer_name": "Kwame Asante", "phone": "+233 24 111 2233",
        "crop": "Soybeans", "region": "Ashanti", "city": "Kumasi",
        "qty_kg": 300, "price_per_kg": 7.20, "grade": "Grade B",
        "available_from": "2025-07-08", "notes": "Cleaned and bagged.",
        "verified": True, "created_at": "2025-06-24",
    },
]

_SEED_BYPRODUCTS = [
    {
        "id": 1, "farmer_id": "farmer_1", "farmer_name": "Kwame Asante",
        "phone": "+233 24 111 2233", "product": "Maize husks",
        "region": "Ashanti", "city": "Kumasi",
        "qty_kg": 800, "price_per_kg": 0.30,
        "use_case": "Animal feed / biogas", "created_at": "2025-06-20",
    },
    {
        "id": 2, "farmer_id": "farmer_3", "farmer_name": "Kofi Boateng",
        "phone": "+233 26 999 0011", "product": "Cassava skins",
        "region": "Eastern", "city": "Koforidua",
        "qty_kg": 400, "price_per_kg": 0.20,
        "use_case": "Animal feed", "created_at": "2025-06-22",
    },
    {
        "id": 3, "farmer_id": "farmer_5", "farmer_name": "Yaw Darko",
        "phone": "+233 27 777 8899", "product": "Rice bran",
        "region": "Northern", "city": "Tamale",
        "qty_kg": 600, "price_per_kg": 0.50,
        "use_case": "Animal feed / oil extraction", "created_at": "2025-06-23",
    },
]

_SEED_DEMAND = [
    {
        "id": 1, "buyer_id": "buyer_1", "buyer_name": "Accra Fresh Ltd",
        "phone": "+233 30 200 1234", "crop": "Tomatoes (local)",
        "region": "Greater Accra", "qty_kg": 500, "max_price_per_kg": 9.00,
        "needed_by": "2025-07-05", "notes": "Weekly recurring order.",
        "created_at": "2025-06-21",
    },
    {
        "id": 2, "buyer_id": "buyer_2", "buyer_name": "North Star Mills",
        "phone": "+233 30 300 5678", "crop": "Maize",
        "region": "Ashanti", "qty_kg": 5000, "max_price_per_kg": 5.00,
        "needed_by": "2025-07-20", "notes": "Feed-grade acceptable.",
        "created_at": "2025-06-20",
    },
    {
        "id": 3, "buyer_id": "buyer_3", "buyer_name": "GhanaCo Exports",
        "phone": "+233 24 456 7890", "crop": "Yam",
        "region": "Brong Ahafo", "qty_kg": 2000, "max_price_per_kg": 6.50,
        "needed_by": "2025-07-25", "notes": "Export quality, pona preferred.",
        "created_at": "2025-06-22",
    },
]

_SEED_ENQUIRIES = [
    {
        "id": 1, "from_user": "buyer_1", "from_name": "Accra Fresh Ltd",
        "from_phone": "+233 30 200 1234", "to_farmer": "farmer_2",
        "to_name": "Abena Mensah", "listing_id": 2,
        "message": "Interested in your tomatoes. Can you do 300kg weekly?",
        "status": "pending", "created_at": "2025-06-22 09:14",
    },
]

_SEED_TRANSPORT = [
    {
        "id": 1, "provider_name": "AgriFast Logistics",
        "phone": "+233 24 800 9000", "whatsapp": "+233 24 800 9000",
        "regions_covered": ["Ashanti", "Greater Accra", "Eastern"],
        "vehicle_types": "10-ton truck, 3-ton pickup",
        "rate_per_km": 2.50, "min_load_kg": 500,
        "notes": "Available Mon–Sat. Cold chain available on request.",
        "verified": True,
    },
    {
        "id": 2, "provider_name": "Northern Haul Co.",
        "phone": "+233 20 700 1122", "whatsapp": "+233 20 700 1122",
        "regions_covered": ["Northern", "Upper East", "Upper West"],
        "vehicle_types": "5-ton truck, motorbike courier",
        "rate_per_km": 1.80, "min_load_kg": 200,
        "notes": "Specialist in Northern region farm pickups.",
        "verified": True,
    },
    {
        "id": 3, "provider_name": "Volta Carriers",
        "phone": "+233 26 600 3344", "whatsapp": "",
        "regions_covered": ["Volta", "Eastern", "Greater Accra"],
        "vehicle_types": "7-ton truck",
        "rate_per_km": 2.10, "min_load_kg": 300,
        "notes": "Cross-Volta bridge specialist route.",
        "verified": False,
    },
]

_SEED_USERS = {
    # Demo accounts: {user_id: {profile}}
    "farmer_1": {
        "id": "farmer_1", "role": "farmer",
        "name": "Kwame Asante", "phone": "+233 24 111 2233",
        "email": "kwame@farm.gh", "password": "farmer1",
        "region": "Ashanti", "city": "Kumasi",
        "farm_size_ha": 12.5, "verified": True,
    },
    "buyer_1": {
        "id": "buyer_1", "role": "buyer",
        "name": "Accra Fresh Ltd", "phone": "+233 30 200 1234",
        "email": "buy@accrafresh.gh", "password": "buyer1",
        "region": "Greater Accra", "city": "Accra",
        "business_type": "Processor", "verified": True,
    },
    "admin_1": {
        "id": "admin_1", "role": "admin",
        "name": "AgriMatch Admin", "email": "admin@agrimatch.gh",
        "password": "admin123",
    },
}


# ── Initialise the store ───────────────────────────────────────────────────────

def init_db():
    """
    Called once per session from utils.init_session().
    Populates st.session_state with seed data if not already present.
    """
    if "agrimatch_db" not in st.session_state:
        st.session_state["agrimatch_db"] = {
            "listings":   list(_SEED_LISTINGS),
            "byproducts": list(_SEED_BYPRODUCTS),
            "demand":     list(_SEED_DEMAND),
            "enquiries":  list(_SEED_ENQUIRIES),
            "transport":  list(_SEED_TRANSPORT),
            "users":      dict(_SEED_USERS),
            # Auto-increment counters for new records
            "_next_listing_id":   len(_SEED_LISTINGS) + 1,
            "_next_byproduct_id": len(_SEED_BYPRODUCTS) + 1,
            "_next_demand_id":    len(_SEED_DEMAND) + 1,
            "_next_enquiry_id":   len(_SEED_ENQUIRIES) + 1,
            "_next_transport_id": len(_SEED_TRANSPORT) + 1,
        }


def _db():
    """Return the live database dict from session state."""
    return st.session_state["agrimatch_db"]


# ── Listings ──────────────────────────────────────────────────────────────────

def get_listings(crop=None, region=None, verified_only=False):
    """Return listings, optionally filtered by crop, region, or verification."""
    rows = _db()["listings"]
    if crop:
        rows = [r for r in rows if r["crop"] == crop]
    if region:
        rows = [r for r in rows if r["region"] == region]
    if verified_only:
        rows = [r for r in rows if r["verified"]]
    return sorted(rows, key=lambda r: r["created_at"], reverse=True)


def add_listing(record: dict):
    """Insert a new listing and return its assigned ID."""
    db = _db()
    record["id"] = db["_next_listing_id"]
    record["created_at"] = datetime.now().strftime("%Y-%m-%d")
    record["verified"] = False          # new listings start unverified
    db["listings"].append(record)
    db["_next_listing_id"] += 1
    return record["id"]


def get_listing_by_id(listing_id: int):
    return next((r for r in _db()["listings"] if r["id"] == listing_id), None)


def get_listings_by_farmer(farmer_id: str):
    return [r for r in _db()["listings"] if r["farmer_id"] == farmer_id]


def delete_listing(listing_id: int, farmer_id: str):
    """Delete a listing owned by the given farmer."""
    db = _db()
    db["listings"] = [
        r for r in db["listings"]
        if not (r["id"] == listing_id and r["farmer_id"] == farmer_id)
    ]


# ── Byproducts ────────────────────────────────────────────────────────────────

def get_byproducts(region=None):
    rows = _db()["byproducts"]
    if region:
        rows = [r for r in rows if r["region"] == region]
    return sorted(rows, key=lambda r: r["created_at"], reverse=True)


def add_byproduct(record: dict):
    db = _db()
    record["id"] = db["_next_byproduct_id"]
    record["created_at"] = datetime.now().strftime("%Y-%m-%d")
    db["byproducts"].append(record)
    db["_next_byproduct_id"] += 1
    return record["id"]


# ── Demand board ──────────────────────────────────────────────────────────────

def get_demand(crop=None, region=None):
    rows = _db()["demand"]
    if crop:
        rows = [r for r in rows if r["crop"] == crop]
    if region:
        rows = [r for r in rows if r["region"] == region]
    return sorted(rows, key=lambda r: r["created_at"], reverse=True)


def add_demand(record: dict):
    db = _db()
    record["id"] = db["_next_demand_id"]
    record["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    db["demand"].append(record)
    db["_next_demand_id"] += 1
    return record["id"]


def get_demand_by_buyer(buyer_id: str):
    return [r for r in _db()["demand"] if r["buyer_id"] == buyer_id]


# ── Enquiries ─────────────────────────────────────────────────────────────────

def get_enquiries_for_farmer(farmer_id: str):
    """All enquiries received by a specific farmer."""
    return [r for r in _db()["enquiries"] if r["to_farmer"] == farmer_id]


def get_enquiries_by_buyer(buyer_id: str):
    """All enquiries sent by a specific buyer."""
    return [r for r in _db()["enquiries"] if r["from_user"] == buyer_id]


def add_enquiry(record: dict):
    db = _db()
    record["id"] = db["_next_enquiry_id"]
    record["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    record["status"] = "pending"
    db["enquiries"].append(record)
    db["_next_enquiry_id"] += 1
    return record["id"]


def update_enquiry_status(enquiry_id: int, status: str):
    """Mark an enquiry as 'responded', 'closed', etc."""
    for r in _db()["enquiries"]:
        if r["id"] == enquiry_id:
            r["status"] = status
            break


# ── Transport ─────────────────────────────────────────────────────────────────

def get_transport(region=None):
    rows = _db()["transport"]
    if region:
        rows = [r for r in rows if region in r.get("regions_covered", [])]
    return rows


def add_transport(record: dict):
    db = _db()
    record["id"] = db["_next_transport_id"]
    record["verified"] = False
    db["transport"].append(record)
    db["_next_transport_id"] += 1
    return record["id"]


# ── Users / Auth ──────────────────────────────────────────────────────────────

def get_user(email: str, password: str):
    """Return user dict if credentials match, else None."""
    for u in _db()["users"].values():
        if u.get("email") == email and u.get("password") == password:
            return u
    return None


def register_user(record: dict):
    """Add a new user. Returns False if email already exists."""
    db = _db()
    for u in db["users"].values():
        if u["email"] == record["email"]:
            return False
    user_id = f"{record['role']}_{len(db['users']) + 1}"
    record["id"] = user_id
    db["users"][user_id] = record
    return user_id


def get_all_users():
    return list(_db()["users"].values())


# ── Admin analytics ───────────────────────────────────────────────────────────

def get_analytics():
    """Aggregate counts and totals for the admin dashboard."""
    db = _db()
    listings   = db["listings"]
    demand     = db["demand"]
    enquiries  = db["enquiries"]
    users      = db["users"]

    return {
        "total_listings":        len(listings),
        "verified_listings":     sum(1 for r in listings if r.get("verified")),
        "total_demand_posts":    len(demand),
        "total_enquiries":       len(enquiries),
        "pending_enquiries":     sum(1 for r in enquiries if r["status"] == "pending"),
        "total_users":           len(users),
        "farmers":               sum(1 for u in users.values() if u.get("role") == "farmer"),
        "buyers":                sum(1 for u in users.values() if u.get("role") == "buyer"),
        "total_supply_kg":       sum(r["qty_kg"] for r in listings),
        "total_demand_kg":       sum(r["qty_kg"] for r in demand),
        "avg_listing_price":     (
            sum(r["price_per_kg"] for r in listings) / len(listings)
            if listings else 0
        ),
        "top_crops":             _top_n([r["crop"] for r in listings], 5),
        "top_regions":           _top_n([r["region"] for r in listings], 5),
        "transport_providers":   len(db["transport"]),
        "byproduct_listings":    len(db["byproducts"]),
    }


def _top_n(items: list, n: int) -> list:
    """Return the top-n most common items as [(item, count), ...]."""
    from collections import Counter
    return Counter(items).most_common(n)
