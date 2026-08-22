"""Unit and headless integration tests for Godot AudioServer bus and effect tools."""

import json
from pathlib import Path

import pytest

from godot_engine_mcp.client.headless_cli import HeadlessCLIClient
from godot_engine_mcp.config import GodotConfig
from godot_engine_mcp.models.audio import (
    ConfigureAudioBusInput,
    GetAudioLayoutInput,
    SetBusEffectInput,
)
from godot_engine_mcp.server import create_server
from godot_engine_mcp.tools.audio_tools import (
    handle_configure_audio_bus,
    handle_get_audio_layout,
    handle_set_bus_effect,
)
from tests.test_tools import MockGodotClient


@pytest.mark.asyncio
async def test_audio_tools_mock() -> None:
    """Test audio tool handlers with MockGodotClient."""
    client = MockGodotClient()

    # 1. Get audio layout
    layout_res = await handle_get_audio_layout(client, GetAudioLayoutInput())
    assert "Audio Buses" in layout_res
    assert "Master" in layout_res
    assert "Music" in layout_res
    assert "Limiter" in layout_res

    # 2. Configure audio bus
    config_res = await handle_configure_audio_bus(
        client,
        ConfigureAudioBusInput(
            bus_name="SFX",
            volume_db=-3.5,
            send_to_bus="Master",
        ),
    )
    assert "SFX" in config_res
    assert "-3.5 dB" in config_res
    assert "Master" in config_res

    # 3. Add audio effect
    effect_res = await handle_set_bus_effect(
        client,
        SetBusEffectInput(
            bus_name="SFX",
            effect_type="AudioEffectReverb",
            properties={"room_size": 0.6, "wet": 0.4},
        ),
    )
    assert "AudioEffectReverb" in effect_res
    assert "SFX" in effect_res
    assert "room_size" in effect_res


@pytest.mark.asyncio
async def test_audio_dynamic_resource() -> None:
    """Test dynamic MCP resource godot://audio/layout."""
    client = MockGodotClient()
    server = create_server(client=client)

    res_raw = await server.read_resource("godot://audio/layout")
    res_list = list(res_raw)
    assert len(res_list) > 0
    content = str(getattr(res_list[0], "content", getattr(res_list[0], "text", "")))
    assert "Master" in content
    payload = json.loads(content)
    assert "buses" in payload
    assert len(payload["buses"]) >= 1


@pytest.mark.asyncio
async def test_audio_headless_execution() -> None:
    """Test headless audio bus layout query and configuration with Godot CLI."""
    exe = GodotConfig.discover_executable()
    if not exe:
        pytest.skip("Godot executable not available.")

    tmp_proj = Path(__file__).parent / ".tmp_audio_proj"
    tmp_proj.mkdir(exist_ok=True)
    try:
        (tmp_proj / "project.godot").write_text(
            'config_version=5\n[application]\nconfig/name="AudioTest"\n',
            encoding="utf-8",
        )
        cfg = GodotConfig(executable_path=exe, project_path=str(tmp_proj))
        client = HeadlessCLIClient(cfg)

        # 1. Query layout headlessly
        layout_res = await handle_get_audio_layout(client, GetAudioLayoutInput())
        assert "Master" in layout_res

        # 2. Configure bus and save layout
        config_res = await handle_configure_audio_bus(
            client,
            ConfigureAudioBusInput(
                bus_name="Music",
                volume_db=-6.0,
                send_to_bus="Master",
                save_layout_path="res://default_bus_layout.tres",
            ),
        )
        assert "Music" in config_res

        layout_file = tmp_proj / "default_bus_layout.tres"
        assert layout_file.exists()
        content = layout_file.read_text(encoding="utf-8")
        assert "AudioBusLayout" in content
    finally:
        import shutil

        shutil.rmtree(tmp_proj, ignore_errors=True)
