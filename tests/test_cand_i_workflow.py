"""
Automated CI Test: C&I Distinct 9-Step Workflow Menu Tree Architecture Test
Per Technical Specification §2.2 & §7.1 & Sprint 1 Structural Fix
Asserts that C&I workflow exists as a distinct 9-step object including Step 9 Permit Package.
"""

import pytest
from app.ui.cand_i_workflow import get_cand_i_workflow_tree, CommercialIndustrialWorkflowTree


def test_cand_i_workflow_tree_distinct_structure():
    tree = get_cand_i_workflow_tree()

    assert isinstance(tree, CommercialIndustrialWorkflowTree)
    assert tree.segment == "COMMERCIAL_INDUSTRIAL"
    assert tree.total_steps == 9
    assert len(tree.workflow_steps) == 9

    step_ids = [step.step_id for step in tree.workflow_steps]
    assert "site_geospatial" in step_ids
    assert "ac_collection_protection" in step_ids
    assert "interconnection_analysis" in step_ids
    assert "procurement_rfq" in step_ids
    assert "cand_i_financial_model" in step_ids
    assert "cand_i_permit_package" in step_ids
