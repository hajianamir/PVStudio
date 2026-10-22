"""
Automated CI Test: RTL Layout Snapshot & Logical Property Validation
Asserts that UI components adhere to logical CSS properties and support dir="rtl".
"""

import pytest
from app.ui.rtl_validator import validate_rtl_layout_properties, simulate_rtl_layout_tree


def test_rtl_logical_properties_pass():
    valid_logical_css = """
    .cockpit-panel {
        margin-inline-start: 1rem;
        padding-inline-end: 2rem;
        inset-inline-start: 0;
    }
    """
    violations = validate_rtl_layout_properties(valid_logical_css)
    assert len(violations) == 0


def test_rtl_physical_properties_fail():
    invalid_physical_css = """
    .cockpit-panel {
        margin-left: 10px;
        padding-right: 20px;
    }
    """
    violations = validate_rtl_layout_properties(invalid_physical_css)
    assert len(violations) > 0


def test_rtl_layout_tree_snapshot():
    rtl_tree = simulate_rtl_layout_tree(direction="rtl")
    assert rtl_tree["direction"] == "rtl"
    assert rtl_tree["root_class"] == "flex-row-reverse"
