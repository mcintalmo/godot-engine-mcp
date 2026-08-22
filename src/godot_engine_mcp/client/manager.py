"""Unified client manager coordinating Live Editor Bridge and Headless CLI fallback."""

from typing import Any

from godot_engine_mcp.client.base import GodotClient
from godot_engine_mcp.client.headless_cli import HeadlessCLIClient
from godot_engine_mcp.client.live_bridge import LiveBridgeClient
from godot_engine_mcp.config import GodotConfig
from godot_engine_mcp.models.common import EngineMode


def _delegate_method(name: str) -> Any:
    async def _method(self: Any, *args: Any, **kwargs: Any) -> Any:
        client = await self.get_active_client()
        target_fn = getattr(client, name)
        return await target_fn(*args, **kwargs)

    _method.__name__ = name
    return _method


class ClientManager(GodotClient):
    """Hybrid client manager that transparently routes to Live Editor or Headless CLI."""

    def __init__(self, config: GodotConfig | None = None) -> None:
        self.config = config or GodotConfig.load()
        self.live_client = LiveBridgeClient(self.config)
        self.headless_client = HeadlessCLIClient(self.config)

    @property
    def mode(self) -> EngineMode:
        return EngineMode.LIVE_EDITOR

    async def is_available(self) -> bool:
        return (
            await self.live_client.is_available()
            or await self.headless_client.is_available()
        )

    async def get_active_client(self) -> GodotClient:
        """Return the best available client (live editor if connected, else headless CLI)."""
        if await self.live_client.is_available():
            return self.live_client
        return self.headless_client

    def __getattr__(self, name: str) -> Any:
        async def _delegated(*args: Any, **kwargs: Any) -> Any:
            client = await self.get_active_client()
            target_fn = getattr(client, name)
            return await target_fn(*args, **kwargs)

        return _delegated


# Satisfy ABC requirements by binding all abstract methods defined in GodotClient
for attr_name in dir(GodotClient):
    if not attr_name.startswith("_") and attr_name not in (
        "mode",
        "is_available",
        "get_active_client",
    ):
        attr = getattr(GodotClient, attr_name)
        if callable(attr):
            setattr(ClientManager, attr_name, _delegate_method(attr_name))

ClientManager.__abstractmethods__ = frozenset()
