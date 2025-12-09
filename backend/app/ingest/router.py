"""
ParserRouter — map tar member names to correct parser functions.

It returns:
    {
        "type": "summary" | "batvol" | "battemp",
        "parser": callable
    }
"""

from typing import Dict, Optional

from ..parsers.summary_parser import parse_summary_csv
from ..parsers.batvol_parser import parse_batvol_csv
from ..parsers.battemp_parser import parse_battemp_csv


class ParserRouter:

    def __init__(self):
        # You can extend this registry dynamically in future.
        self.routes = [
            ("summary", "summary", parse_summary_csv),
            ("batvol", "batvol", parse_batvol_csv),
            ("battemp", "battemp", parse_battemp_csv),
        ]

    def resolve(self, member_name: str) -> Optional[Dict]:
        name = member_name.lower()

        for key, typ, func in self.routes:
            if key in name:
                return {
                    "type": typ,
                    "parser": func,
                }

        return None  # this member has no parser (ignored)
