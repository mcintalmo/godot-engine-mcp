"""Unit and headless tests for Godot Phase 18 tools (Camera Presets, High-Res Viewport Capture & Rendering Pipeline)."""

import pytest

from godot_engine_mcp.client.headless_cli import HeadlessCLIClient
from godot_engine_mcp.config import GodotConfig
from godot_engine_mcp.models.camera_rendering import (
    CaptureViewportInput,
    ConfigureCameraInput,
    ConfigureRenderSettingsInput,
)
from godot_engine_mcp.tools.camera_rendering_tools import (
    handle_capture_viewport,
    handle_configure_camera,
    handle_configure_render_settings,
)
from tests.test_tools import MockGodotClient


@pytest.mark.asyncio
async def test_phase18_tools_mock() -> None:
    """Test Phase 18 tools with MockGodotClient."""
    client = MockGodotClient()

    # 1. Configure Camera
    cam_res = await handle_configure_camera(
        client,
        ConfigureCameraInput(
            camera_node_path="MainCamera",
            projection="perspective",
            fov=80.0,
            current=True,
        ),
    )
    assert "Configured Camera" in cam_res
    assert "MainCamera" in cam_res
    assert "FOV: 80.0 deg" in cam_res

    # 2. Configure Render Settings
    render_res = await handle_configure_render_settings(
        client,
        ConfigureRenderSettingsInput(
            msaa_3d="4x",
            screen_space_aa="fxaa",
            use_taa=True,
            scaling_3d_mode="fsr2",
        ),
    )
    assert "Configured render settings" in render_res
    assert "MSAA 3D: 4x" in render_res
    assert "Screen-Space AA: fxaa" in render_res

    # 3. Capture Viewport
    shot_res = await handle_capture_viewport(
        client,
        CaptureViewportInput(
            max_width=1280,
            max_height=720,
            format="png",
            include_base64=True,
        ),
    )
    assert "Viewport Captured" in shot_res
    assert "1280x720" in shot_res
    assert "Base64 Payload Included" in shot_res


@pytest.mark.asyncio
async def test_phase18_headless_client(tmp_path: pytest.TempPathFactory) -> None:
    """Test Phase 18 tools with HeadlessCLIClient."""
    cfg = GodotConfig(project_path=str(tmp_path))
    client = HeadlessCLIClient(cfg)

    # 1. Configure Camera headlessly
    cam_res = await handle_configure_camera(
        client,
        ConfigureCameraInput(
            camera_node_path="Camera3D",
            fov=75.0,
        ),
    )
    assert "Configured Camera" in cam_res
    assert "Camera3D" in cam_res

    # 2. Configure Render Settings headlessly
    render_res = await handle_configure_render_settings(
        client,
        ConfigureRenderSettingsInput(
            msaa_3d="2x",
        ),
    )
    assert "Configured render settings" in render_res
    assert "MSAA 3D: 2x" in render_res

    # 3. Capture Viewport headlessly
    shot_res = await handle_capture_viewport(
        client,
        CaptureViewportInput(
            max_width=640,
            max_height=360,
        ),
    )
    assert "Viewport Captured" in shot_res
    assert "640x360" in shot_res
