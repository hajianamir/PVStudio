"""
RTL Layout Validator & Snapshot Test Infrastructure
Per Phase 1 Technical Specification §3.4 & Gate Criterion G7
"""

import re
from typing import List, Dict, Any


def validate_rtl_layout_properties(css_content: str) -> List[str]:
    """
    Scans CSS/HTML styles for non-RTL compliant physical properties (e.g. margin-left, padding-right).
    Returns list of violations that should be refactored to logical properties.
    """
    forbidden_physical_properties = [
        r"\bmargin-left\b",
        r"\bmargin-right\b",
        r"\bpadding-left\b",
        r"\bpadding-right\b",
        r"\bleft\s*:",
        r"\bright\s*:"
    ]

    violations = []
    for prop in forbidden_physical_properties:
        matches = re.findall(prop, css_content, re.IGNORECASE)
        if matches:
            violations.extend(matches)

    return violations


def simulate_rtl_layout_tree(direction: str = "ltr") -> Dict[str, Any]:
    """
    Generates layout component tree snapshot for RTL testing.
    """
    return {
        "direction": direction,
        "root_class": "flex-row-reverse" if direction == "rtl" else "flex-row",
        "sidebar_align": "start" if direction == "rtl" else "left",
        "logical_margin_inline_start": "1rem"
    }
