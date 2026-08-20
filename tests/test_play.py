"""Unit and headless tests for Godot Play Mode and debug control tools."""

import pytest

from godot_mcp.client.headless_cli import HeadlessCLIClient
from godot_mcp.config import GodotConfig
from godot_mcp.models.play import (
    GetPlayStateInput,
    PlaySceneInput,
    PlaySceneMode,
    SetPlayStateInput,
    StopSceneInput,
)
from godot_mcp.tools.play_tools import (
    handle_get_play_state,
    handle_play_scene,
    handle_set_play_state,
    handle_stop_scene,
)
from tests.test_tools import MockGodotClient


@pytest.mark.asyncio
async def test_play_tools_mock() -> None:
    """Test play tool handlers with MockGodotClient."""
    client = MockGodotClient()

    # 1. Play scene
    play_res = await handle_play_scene(
        client,
        PlaySceneInput(mode=PlaySceneMode.MAIN),
    )
    assert "PLAYING" in play_res or "Playing" in play_res
    assert "main" in play_res

    # 2. Get play state
    state_res = await handle_get_play_state(client, GetPlayStateInput())
    assert "Play State" in state_res
    assert "Time Scale" in state_res or "Simulation Speed" in state_res

    # 3. Set play state (time_scale + pause)
    set_res = await handle_set_play_state(
        client,
        SetPlayStateInput(pause=True, time_scale=0.5, step_frames=2),
    )
    assert "0.5x" in set_res or "0.5" in set_res
    assert "True" in set_res or "true" in set_res

    # 4. Stop scene
    stop_res = await handle_stop_scene(client, StopSceneInput())
    assert "Stopped" in stop_res or "STOPPED" in stop_res


@pytest.mark.asyncio
async def test_play_headless_client() -> None:
    """Test play mode handling in HeadlessCLIClient."""
    cfg = GodotConfig()
    client = HeadlessCLIClient(cfg)

    # 1. Play scene in headless mode provides actionable hint
    play_res = await handle_play_scene(
        client,
        PlaySceneInput(mode=PlaySceneMode.CURRENT),
    )
    assert "requires Godot Editor" in play_res or "Live Bridge" in play_res

    # 2. Get play state
    state_res = await handle_get_play_state(client, GetPlayStateInput())
    assert "STOPPED" in state_res

    # 3. Set play state
    set_res = await handle_set_play_state(
        client,
        SetPlayStateInput(time_scale=2.0),
    )
    assert "2.0x" in set_res or "2.0" in set_res
