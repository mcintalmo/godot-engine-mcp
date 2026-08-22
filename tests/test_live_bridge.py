"""Unit tests for live bridge and mock client operations."""

import pytest

from godot_engine_mcp.client.live_bridge import LiveBridgeClient
from godot_engine_mcp.config import GodotConfig
from godot_engine_mcp.models.common import EngineMode


@pytest.mark.asyncio
async def test_live_bridge_unavailable_when_offline(mock_config: GodotConfig) -> None:
    """Test that is_available returns False when Godot is not running."""
    # Point to an unused port
    mock_config.bridge_port = 39999
    client = LiveBridgeClient(mock_config)

    is_avail = await client.is_available()
    assert is_avail is False


@pytest.mark.asyncio
async def test_live_bridge_rpc_error_handling(mock_config: GodotConfig) -> None:
    """Test error response when sending RPC to offline port."""
    mock_config.bridge_port = 39999
    client = LiveBridgeClient(mock_config)

    res = await client.get_version()
    assert res.success is False
    assert res.error_code == "DISCONNECTED"
    assert res.mode == EngineMode.LIVE_EDITOR
    assert "godot_mcp" in (res.actionable_hint or "")
