"""
Mock Stripe + HubSpot data for a multi-location GPO member scenario.
Intentionally generic — works for dental, vet, HVAC, or any vertical
where members have multiple practice/shop locations.
In production this is replaced by live API calls to both platforms.
"""

STRIPE_CUSTOMERS = [
    {"stripe_customer_id": "cus_AAA001", "name": "Apex Practice Group",   "email": "billing@apexpractice.com"},
    {"stripe_customer_id": "cus_BBB002", "name": "Meridian Partners - Main",    "email": "admin@meridianpartners.com"},
    {"stripe_customer_id": "cus_BBB003", "name": "Meridian Partners - East",    "email": "admin@meridianpartners.com"},
    {"stripe_customer_id": "cus_CCC004", "name": "Bright Path Clinic",    "email": "billing@brightpathclinic.io"},
    {"stripe_customer_id": "cus_DDD005", "name": "Sunrise Group - HQ",    "email": "ops@sunrisegroup.com"},
    {"stripe_customer_id": "cus_DDD006", "name": "Sunrise Group - West",  "email": "ops@sunrisegroup.com"},
    {"stripe_customer_id": "cus_DDD007", "name": "Sunrise Group - North", "email": "ops@sunrisegroup.com"},
    {"stripe_customer_id": "cus_EEE008", "name": "Family First Practice", "email": "hello@familyfirstpractice.com"},
]

STRIPE_SUBSCRIPTIONS = [
    {"stripe_sub_id": "sub_001", "stripe_customer_id": "cus_AAA001", "status": "active",   "mrr": 299, "plan": "Pro",     "current_period_end": "2026-06-15", "past_due": False},
    {"stripe_sub_id": "sub_002", "stripe_customer_id": "cus_AAA001", "status": "active",   "mrr": 299, "plan": "Pro",     "current_period_end": "2026-06-15", "past_due": False},
    {"stripe_sub_id": "sub_003", "stripe_customer_id": "cus_AAA001", "status": "active",   "mrr": 299, "plan": "Pro",     "current_period_end": "2026-06-15", "past_due": False},
    {"stripe_sub_id": "sub_004", "stripe_customer_id": "cus_BBB002", "status": "active",   "mrr": 299, "plan": "Pro",     "current_period_end": "2026-06-20", "past_due": False},
    {"stripe_sub_id": "sub_005", "stripe_customer_id": "cus_BBB003", "status": "past_due", "mrr": 299, "plan": "Pro",     "current_period_end": "2026-05-20", "past_due": True},
    {"stripe_sub_id": "sub_006", "stripe_customer_id": "cus_CCC004", "status": "active",   "mrr": 199, "plan": "Starter", "current_period_end": "2026-06-10", "past_due": False},
    {"stripe_sub_id": "sub_007", "stripe_customer_id": "cus_DDD005", "status": "active",   "mrr": 299, "plan": "Pro",     "current_period_end": "2026-06-25", "past_due": False},
    {"stripe_sub_id": "sub_008", "stripe_customer_id": "cus_DDD006", "status": "active",   "mrr": 299, "plan": "Pro",     "current_period_end": "2026-06-25", "past_due": False},
    {"stripe_sub_id": "sub_009", "stripe_customer_id": "cus_DDD007", "status": "canceled", "mrr": 0,   "plan": "Pro",     "current_period_end": "2026-05-01", "past_due": False},
    {"stripe_sub_id": "sub_010", "stripe_customer_id": "cus_EEE008", "status": "active",   "mrr": 199, "plan": "Starter", "current_period_end": "2026-06-18", "past_due": False},
]

HUBSPOT_COMPANIES = [
    {"hs_company_id": "HS-1001", "name": "Apex Practice Group",   "domain": "apexpractice.com",        "owner": "Alex R."},
    {"hs_company_id": "HS-1002", "name": "Meridian Partners",     "domain": "meridianpartners.com",    "owner": "Sam K."},
    {"hs_company_id": "HS-1003", "name": "Bright Path Clinic",    "domain": "brightpathclinic.io",     "owner": "Alex R."},
    {"hs_company_id": "HS-1004", "name": "Sunrise Group",         "domain": "sunrisegroup.com",        "owner": "Sam K."},
    {"hs_company_id": "HS-1005", "name": "Family First Practice", "domain": "familyfirstpractice.com", "owner": "Alex R."},
]

HUBSPOT_LOCATIONS = [
    {"hs_location_id": "LOC-101", "hs_company_id": "HS-1001", "name": "Apex - Main St"},
    {"hs_location_id": "LOC-102", "hs_company_id": "HS-1001", "name": "Apex - North"},
    {"hs_location_id": "LOC-103", "hs_company_id": "HS-1001", "name": "Apex - Eastside"},
    {"hs_location_id": "LOC-104", "hs_company_id": "HS-1002", "name": "Meridian - Main"},
    {"hs_location_id": "LOC-105", "hs_company_id": "HS-1002", "name": "Meridian - East"},
    {"hs_location_id": "LOC-106", "hs_company_id": "HS-1003", "name": "Bright Path - Downtown"},
    {"hs_location_id": "LOC-107", "hs_company_id": "HS-1004", "name": "Sunrise - Westlake"},
    {"hs_location_id": "LOC-108", "hs_company_id": "HS-1004", "name": "Sunrise - Midtown"},
    {"hs_location_id": "LOC-109", "hs_company_id": "HS-1004", "name": "Sunrise - Main (Canceled)"},
    {"hs_location_id": "LOC-110", "hs_company_id": "HS-1005", "name": "Family First - Oak Ave"},
]

# Canonical mapping table: the data spine linking Stripe ↔ HubSpot
MAPPING_TABLE = [
    {"stripe_sub_id": "sub_001", "stripe_customer_id": "cus_AAA001", "hs_location_id": "LOC-101", "hs_company_id": "HS-1001"},
    {"stripe_sub_id": "sub_002", "stripe_customer_id": "cus_AAA001", "hs_location_id": "LOC-102", "hs_company_id": "HS-1001"},
    {"stripe_sub_id": "sub_003", "stripe_customer_id": "cus_AAA001", "hs_location_id": "LOC-103", "hs_company_id": "HS-1001"},
    {"stripe_sub_id": "sub_004", "stripe_customer_id": "cus_BBB002", "hs_location_id": "LOC-104", "hs_company_id": "HS-1002"},
    {"stripe_sub_id": "sub_005", "stripe_customer_id": "cus_BBB003", "hs_location_id": "LOC-105", "hs_company_id": "HS-1002"},
    {"stripe_sub_id": "sub_006", "stripe_customer_id": "cus_CCC004", "hs_location_id": "LOC-106", "hs_company_id": "HS-1003"},
    {"stripe_sub_id": "sub_007", "stripe_customer_id": "cus_DDD005", "hs_location_id": "LOC-107", "hs_company_id": "HS-1004"},
    {"stripe_sub_id": "sub_008", "stripe_customer_id": "cus_DDD006", "hs_location_id": "LOC-108", "hs_company_id": "HS-1004"},
    {"stripe_sub_id": "sub_009", "stripe_customer_id": "cus_DDD007", "hs_location_id": "LOC-109", "hs_company_id": "HS-1004"},
    {"stripe_sub_id": "sub_010", "stripe_customer_id": "cus_EEE008", "hs_location_id": "LOC-110", "hs_company_id": "HS-1005"},
]
