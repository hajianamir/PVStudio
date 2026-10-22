"""
Automated CI Test: C&I Distinct 8-Step Workflow Menu Tree Architecture Test
Per Technical Specification §2.2 & §7.1
Asserts that C&I workflow exists as a distinct 8-step object independent of the Residential 5-step workflow.
"""

import pytest
from app.ui.cand_i_workflow import get_cand_i_workflow_tree, CommercialIndustrialWorkflowTree


def test_cand_i_workflow_tree_distinct_structure():
    tree = get_cand_i_workflow_tree()

    assert isinstance(tree, CommercialIndustrialWorkflowTree)
    assert tree.segment == "COMMERCIAL_INDUSTRIAL"
    assert tree.total_steps == 8
    assert len(tree.workflow_steps) == 8

    step_ids = [step.step_id for step in tree.workflow_steps]
    assert "site_geospatial" in step_ids
    assert "ac_collection_protection" in step_ids
    assert "interconnection_analysis" in step_ids
    assert "procurement_rfq" in step_ids
    assert "cand_i_financial_model" in step_ids
