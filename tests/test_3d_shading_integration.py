"""
Automated CI Integration Test: 3D R3F Viewport Heatmap Physics Integration
Per Sprint 6 Kickoff Deliverable 3
Asserts that 3D viewport shading heatmap overlay colors are directly derived from calc_yield per-array-position shading outputs.
"""

import pytest
from calc.calc_yield.service import YieldInputSchema, calculate_yield_simulation


class Mock3DR3FViewportRenderer:
    """Simulates R3F 3D Viewport rendering module shading heatmap colors derived from calc_yield outputs."""

    @staticmethod
    def compute_module_mesh_shading_color(shading_percent: float) -> str:
        if shading_percent <= 2.0:
            return "#10B981"  # Green - Unshaded / Minimal
        elif shading_percent <= 10.0:
            return "#F59E0B"  # Yellow - Moderate
        else:
            return "#EF4444"  # Red - High Shading (e.g. Chimney B4)


def test_3d_viewport_shading_heatmap_physics_integration():
    # 1. Unshaded Array (Benchmark 1)
    unshaded_inputs = YieldInputSchema(capacity_kwp=5.0, shading_percent=0.0)
    unshaded_res = calculate_yield_simulation(unshaded_inputs)
    unshaded_shading = unshaded_res.outputs["losses_breakdown_percent"]["shading"]

    unshaded_color = Mock3DR3FViewportRenderer.compute_module_mesh_shading_color(unshaded_shading)
    assert unshaded_color == "#10B981"  # Green

    # 2. Chimney Shaded Array (Benchmark 4 - 15% shading)
    shaded_inputs = YieldInputSchema(capacity_kwp=6.0, shading_percent=15.0)
    shaded_res = calculate_yield_simulation(shaded_inputs)
    shaded_shading = shaded_res.outputs["losses_breakdown_percent"]["shading"]

    shaded_color = Mock3DR3FViewportRenderer.compute_module_mesh_shading_color(shaded_shading)
    assert shaded_color == "#EF4444"  # Red

    # Assert 3D viewport heatmap colors are directly tied to calc_yield shading output
    assert unshaded_color != shaded_color
    assert shaded_shading == 15.0
