from . import benco, henry_schein, base86, darby, patterson, vetcove, auto_detect

ADAPTERS = {
    "Benco": benco.parse,
    "Henry Schein": henry_schein.parse,
    "Base86": base86.parse,
    "Darby": darby.parse,
    "Patterson": patterson.parse,
    "Vetcove": vetcove.parse,
}
