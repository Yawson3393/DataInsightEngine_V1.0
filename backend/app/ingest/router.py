# backend/app/ingest/router.py
from typing import Dict, Callable
from ..parsers import summary_parser, batvol_parser, battemp_parser

PARSERS = {
    "summary": summary_parser.parse,
    "batvol": batvol_parser.parse,
    "battemp": battemp_parser.parse
}

def route(member_name: str):
    n = member_name.lower()
    if "summary" in n:
        return PARSERS["summary"]
    if "batvol" in n or "bat_vol" in n:
        return PARSERS["batvol"]
    if "battemp" in n or "bat_temp" in n:
        return PARSERS["battemp"]
    return None
