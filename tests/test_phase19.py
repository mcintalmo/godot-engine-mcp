"""Unit and headless tests for Godot Phase 19 tools (Interactive Runtime Input Simulation & Debug Drawing)."""

import pytest

from godot_mcp.client.headless_cli import HeadlessCLIClient
from godot_mcp.config import GodotConfig
from godot_mcp.models.input_simulation import (
    ClearDebugShapesInput,
    DebugShape,
    DrawDebugShapesInput,
    SimulateInputInput,
)
from godot_mcp.tools.input_simulation_tools import (
    handle_clear_debug_shapes,
    handle_draw_debug_shapes,
    handle_simulate_input,
)
from tests.test_tools import MockGodotClient


@pytest.mark.asyncio
async def test_phase19_tools_mock() -> None:
    """Test Phase 19 tools with MockGodotClient."""
    client = MockGodotClient()

    # 1. Simulate Input Action
    act_res = await handle_simulate_input(
        client,
        SimulateInputInput(
            event_type="action",
            action="jump",
            pressed=True,
        ),
    )
    assert "Dispatched Input Event" in act_res
    assert "jump" in act_res
    assert "Pressed" in act_res

    # 2. Draw Debug Shapes
    draw_res = await handle_draw_debug_shapes(
        client,
        DrawDebugShapesInput(
            shapes=[
                DebugShape(
                    shape_type="line_3d",
                    start=[0.0, 0.0, 0.0],
                    end=[0.0, 10.0, 0.0],
                    color=[1.0, 0.0, 0.0, 1.0],
                    duration=5.0,
                ),
                DebugShape(
                    shape_type="circle_2d",
                    position=[100.0, 100.0],
                    radius=50.0,
                    duration=3.0,
                ),
            ]
        ),
    )
    assert "Rendered 2 Debug Shapes" in draw_res
    assert "3D Shapes" in draw_res
    assert "2D Shapes" in draw_res

    # 3. Clear Debug Shapes
    clear_res = await handle_clear_debug_shapes(
        client,
        ClearDebugShapesInput(),
    )
    assert "Cleared Debug Overlays" in clear_res
    assert "Shapes Removed" in clear_res


@pytest.mark.asyncio
async def test_phase19_headless_client(tmp_path: pytest.TempPathFactory) -> None:
    """Test Phase 19 tools with HeadlessCLIClient."""
    cfg = GodotConfig(project_path=str(tmp_path))
    client = HeadlessCLIClient(cfg)

    # 1. Simulate Input Key headlessly
    key_res = await handle_simulate_input(
        client,
        SimulateInputInput(
            event_type="key",
            key="Space",
            pressed=True,
        ),
    )
    assert "Dispatched Input Event" in key_res
    assert "Space" in key_res

    # 2. Draw Debug Shapes headlessly
    draw_res = await handle_draw_debug_shapes(
        client,
        DrawDebugShapesInput(
            shapes=[
                DebugShape(
                    shape_type="box_3d",
                    position=[0.0, 0.0, 0.0],
                    size=[2.0, 2.0, 2.0],
                )
            ]
        ),
    )
    assert "Rendered 1 Debug Shapes" in draw_res
    assert "3D Shapes" in draw_res

    # 3. Clear Debug Shapes headlessly
    clear_res = await handle_clear_debug_shapes(
        client,
        ClearDebugShapesInput(),
    )
    assert "Cleared Debug Overlays" in clear_res
