from . import benco, henry_schein, base86, darby, patterson, vetcove, ferguson, sysco, vsp, auto_detect

ADAPTERS = {
    # Dental
    "Benco": benco.parse,
    "Henry Schein": henry_schein.parse,
    "Base86": base86.parse,
    "Darby": darby.parse,
    "Patterson": patterson.parse,
    # Veterinary
    "Vetcove": vetcove.parse,
    # HVAC
    "Ferguson": ferguson.parse,
    # Restaurant / foodservice
    "Sysco": sysco.parse,
    # Optometry
    "VSP/Essilor": vsp.parse,
}

# Which vertical each adapter belongs to — used to auto-load the right UOM table.
ADAPTER_VERTICAL = {
    "Benco": "dental",
    "Henry Schein": "dental",
    "Base86": "dental",
    "Darby": "dental",
    "Patterson": "dental",
    "Vetcove": "vet",
    "Ferguson": "hvac",
    "Sysco": "restaurant",
    "VSP/Essilor": "optometry",
}
