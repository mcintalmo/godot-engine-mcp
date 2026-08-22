"""Unit and headless tests for Godot Phase 29 tools (OpenXR & Spatial Computing)."""

import pytest

from godot_engine_mcp.client.headless_cli import HeadlessCLIClient
from godot_engine_mcp.config import GodotConfig
from godot_engine_mcp.models.openxr import (
    ConfigureXRPassthroughInput,
    SetupXRRigInput,
)
from godot_engine_mcp.tools.openxr_tools import (
    handle_configure_xr_passthrough,
    handle_setup_xr_rig,
)
from tests.test_tools import MockGodotClient


@pytest.mark.asyncio
async def test_phase29_tools_mock() -> None:
    """Test Phase 29 tools with MockGodotClient."""
    client = MockGodotClient()

    # 1. Setup XR Rig
    rig_res = await handle_setup_xr_rig(
        client,
        SetupXRRigInput(
            rig_name="PlayerXROrigin",
            enable_controllers=True,
            enable_hand_tracking=True,
            action_map_path="res://actions.tres",
        ),
    )
    assert "Scaffolded OpenXR Rig" in rig_res
    assert "PlayerXROrigin" in rig_res
    assert "LeftHand" in rig_res
    assert "RightHandTracking" in rig_res
    assert "actions.tres" in rig_res

    # 2. Configure XR Passthrough
    pt_res = await handle_configure_xr_passthrough(
        client,
        ConfigureXRPassthroughInput(
            xr_origin_path="PlayerXROrigin",
            enable_passthrough=True,
            reference_space="stage",
            foveated_rendering_level="high",
            dynamic_foveation=True,
        ),
    )
    assert "Configured OpenXR Spatial Settings" in pt_res
    assert "PlayerXROrigin" in pt_res
    assert "STAGE" in pt_res
    assert "HIGH" in pt_res


@pytest.mark.asyncio
async def test_phase29_headless_client(tmp_path: pytest.TempPathFactory) -> None:
    """Test Phase 29 tools with HeadlessCLIClient."""
    cfg = GodotConfig(project_path=str(tmp_path))
    client = HeadlessCLIClient(cfg)

    # 1. Setup XR Rig headlessly
    rig_res = await handle_setup_xr_rig(
        client,
        SetupXRRigInput(rig_name="XROrigin3D"),
    )
    assert "Scaffolded OpenXR Rig" in rig_res
    assert "XRCamera3D" in rig_res

    # 2. Configure XR Passthrough headlessly
    pt_res = await handle_configure_xr_passthrough(
        client,
        ConfigureXRPassthroughInput(
            xr_origin_path="XROrigin3D",
            reference_space="local_floor",
        ),
    )
    assert "Configured OpenXR Spatial Settings" in pt_res
    assert "LOCAL_FLOOR" in pt_res
