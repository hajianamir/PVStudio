"""
RTL Layout Static Code Scanner & Snapshot Test Infrastructure
Per Phase 1 Technical Specification §3.4 & Gate Criterion G7
Statically scans UI source code files (.tsx, .jsx, .css, .scss) for forbidden directional physical properties.
"""

import re
import os
from typing import List, Dict, Any


FORBIDDEN_PHYSICAL_PATTERNS = [
    (r"\bmargin-left\b", "Use margin-inline-start instead"),
    (r"\bmargin-right\b", "Use margin-inline-end instead"),
    (r"\bpadding-left\b", "Use padding-inline-start instead"),
    (r"\bpadding-right\b", "Use padding-inline-end instead"),
    (r"\bleft\s*:", "Use inset-inline-start or logical positioning instead"),
    (r"\bright\s*:", "Use inset-inline-end or logical positioning instead"),
    (r"\btext-align\s*:\s*(left|right)", "Use text-align: start or text-align: end instead"),
    (r"\bborder-left\b", "Use border-inline-start instead"),
    (r"\bborder-right\b", "Use border-inline-end instead"),
]


def scan_file_for_rtl_violations(file_content: str, filename: str = "snippet") -> List[Dict[str, Any]]:
    """
    Statically scans UI code content for non-RTL compliant physical properties.
    """
    violations = []
    lines = file_content.splitlines()

    for line_idx, line in enumerate(lines, 1):
        # Ignore comments or inline whitelisted bypass comments if needed
        if "/* rtl-ignore */" in line or "// rtl-ignore" in line:
            continue

        for pattern, recommendation in FORBIDDEN_PHYSICAL_PATTERNS:
            matches = re.finditer(pattern, line, re.IGNORECASE)
            for m in matches:
                violations.append({
                    "file": filename,
                    "line": line_idx,
                    "matched": m.group(0),
                    "recommendation": recommendation,
                    "snippet": line.strip()
                })

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
