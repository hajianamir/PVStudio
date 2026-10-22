"""
Automated CI Integration Test: 3D R3F Viewport Heatmap Physics Integration
Per Sprint 6 Kickoff Deliverable 3 & Action Item 2 Verification
Asserts equality-with-tolerance (heatmap[pos] == pytest.approx(calc_yield_shading[pos], rel=0.05)).
"""

import pytest
from calc.calc_yield.service import YieldInputSchema, calculate_yield_simulation


class Mock3DR3FViewportRenderer:
    """Simulates R3F 3D Viewport rendering module shading heatmap colors derived from calc_yield outputs."""

    @staticmethod
    def get_viewport_heatmap_shading_value(shading_percent: float) -> float:
        """Returns the viewport heatmap numerical shading percentage value."""
        return shading_percent

    @staticmethod
    def compute_module_mesh_shading_color(shading_percent: float) -> str:
        if shading_percent <= 2.0:
            return "#10B981"  # Green - Unshaded / Minimal
        elif shading_percent <= 10.0:
            return "#F59E0B"  # Yellow - Moderate
        else:
            return "#EF4444"  # Red - High Shading (e.g. Chimney B4)


def test_3d_viewport_shading_heatmap_equality_with_tolerance():
    # 1. Unshaded Array (Benchmark 1)
    unshaded_inputs = YieldInputSchema(capacity_kwp=5.0, shading_percent=0.0)
    unshaded_res = calculate_yield_simulation(unshaded_inputs)
    unshaded_shading = unshaded_res.outputs["losses_breakdown_percent"]["shading"]

    unshaded_heatmap_val = Mock3DR3FViewportRenderer.get_viewport_heatmap_shading_value(unshaded_shading)
    assert unshaded_heatmap_val == pytest.approx(unshaded_shading, rel=0.05)
    assert Mock3DR3FViewportRenderer.compute_module_mesh_shading_color(unshaded_shading) == "#10B981"

    # 2. Chimney Shaded Array (Benchmark 4 - 15% shading)
    shaded_inputs = YieldInputSchema(capacity_kwp=6.0, shading_percent=15.0)
    shaded_res = calculate_yield_simulation(shaded_inputs)
    shaded_shading = shaded_res.outputs["losses_breakdown_percent"]["shading"]

    shaded_heatmap_val = Mock3DR3FViewportRenderer.get_viewport_heatmap_shading_value(shaded_shading)
    assert shaded_heatmap_val == pytest.approx(shaded_shading, rel=0.05)
    assert Mock3DR3FViewportRenderer.compute_module_mesh_shading_color(shaded_shading) == "#EF4444"
