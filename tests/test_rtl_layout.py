"""
Automated CI Test: RTL Layout Static Scanner & Logical Property Validation
Per Phase 1 Technical Specification §3.4 & Gate Criterion G7
Asserts that static scan fails build if hardcoded physical directional properties are present.
"""

import pytest
from app.ui.rtl_validator import scan_file_for_rtl_violations, simulate_rtl_layout_tree


def test_rtl_static_scan_clean_code_passes():
    valid_logical_css = """
    .cockpit-panel {
        margin-inline-start: 1rem;
        padding-inline-end: 2rem;
        inset-inline-start: 0;
        text-align: start;
    }
    """
    violations = scan_file_for_rtl_violations(valid_logical_css, "panel.css")
    assert len(violations) == 0


def test_rtl_static_scan_violations_detected():
    invalid_physical_css = """
    .cockpit-panel {
        margin-left: 10px;
        padding-right: 20px;
        text-align: left;
    }
    """
    violations = scan_file_for_rtl_violations(invalid_physical_css, "bad_panel.css")
    assert len(violations) == 3
    assert violations[0]["matched"] == "margin-left"
    assert violations[1]["matched"] == "padding-right"
    assert violations[2]["matched"] == "text-align: left"


def test_rtl_static_scan_ignore_comment_works():
    ignored_physical_css = """
    .cockpit-panel {
        margin-left: 10px; // rtl-ignore
    }
    """
    violations = scan_file_for_rtl_violations(ignored_physical_css, "ignored.css")
    assert len(violations) == 0


def test_rtl_layout_tree_snapshot():
    rtl_tree = simulate_rtl_layout_tree(direction="rtl")
    assert rtl_tree["direction"] == "rtl"
    assert rtl_tree["root_class"] == "flex-row-reverse"
