"""Live Editor Bridge client communicating with Godot EditorPlugin via WebSocket."""

import asyncio
import inspect
import json
import logging
import uuid
from typing import Any

from websockets.asyncio.client import connect
from websockets.exceptions import WebSocketException

from godot_mcp.client.base import GodotClient
from godot_mcp.client.lsp_client import GodotLSPClient
from godot_mcp.config import GodotConfig
from godot_mcp.models.common import EngineMode, StandardResult

logger = logging.getLogger(__name__)


def _create_rpc_forwarder(name: str, sig: inspect.Signature | None) -> Any:
    """Generate dynamic JSON-RPC forwarder based on GodotClient method signature."""

    async def _forwarder(self: Any, *args: Any, **kwargs: Any) -> StandardResult:
        params: dict[str, Any] = {}
        if sig:
            try:
                bound = sig.bind_partial(self, *args, **kwargs)
                bound.apply_defaults()
                params = {
                    k: v
                    for k, v in bound.arguments.items()
                    if k != "self" and v is not None
                }
            except TypeError:
                params = dict(kwargs)
        else:
            params = dict(kwargs)
        return await self._send_rpc(name, params)

    _forwarder.__name__ = name
    return _forwarder


class LiveBridgeClient(GodotClient):
    """Client for communicating with the live Godot Editor via the godot_mcp addon."""

    def __init__(self, config: GodotConfig | None = None) -> None:
        self.config = config or GodotConfig.load()
        self.uri = f"ws://{self.config.bridge_host}:{self.config.bridge_port}"
        self.lsp = GodotLSPClient(self.config)

    @property
    def mode(self) -> EngineMode:
        return EngineMode.LIVE_EDITOR

    async def is_available(self) -> bool:
        """Check if the Godot Editor bridge server is responding."""
        try:
            async with asyncio.timeout(1.5):
                async with connect(self.uri) as ws:
                    req = {
                        "jsonrpc": "2.0",
                        "id": "ping",
                        "method": "ping",
                        "params": {},
                    }
                    await ws.send(json.dumps(req))
                    resp_raw = await ws.recv()
                    data = json.loads(resp_raw)
                    return (
                        data.get("result", {}).get("pong", False)
                        or data.get("id") == "ping"
                    )
        except (
            WebSocketException,
            OSError,
            TimeoutError,
            json.JSONDecodeError,
        ) as e:
            logger.debug("is_available check failed: %s", e)
            return False

    async def _send_rpc(
        self, method: str, params: dict[str, Any] | None = None
    ) -> StandardResult:
        """Send a JSON-RPC request to the running Godot Editor bridge."""
        req_id = str(uuid.uuid4())
        payload = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": method,
            "params": params or {},
        }

        try:
            async with asyncio.timeout(self.config.request_timeout):
                async with connect(self.uri) as ws:
                    await ws.send(json.dumps(payload))
                    resp_text = await ws.recv()

                    resp_data = json.loads(resp_text)

                    if "error" in resp_data:
                        err = resp_data["error"]
                        return StandardResult(
                            success=False,
                            message=err.get("message", "Editor bridge error"),
                            mode=self.mode,
                            data=err.get("data", {}),
                            error_code=str(err.get("code", "BRIDGE_ERROR")),
                            actionable_hint="Check that the active scene is valid in Godot Editor.",
                        )

                    result_data = resp_data.get("result", {})
                    return StandardResult(
                        success=result_data.get("success", True),
                        message=result_data.get(
                            "message", f"Operation '{method}' succeeded"
                        ),
                        mode=self.mode,
                        data=result_data.get("data", result_data),
                        warnings=result_data.get("warnings", []),
                    )

        except TimeoutError:
            return StandardResult(
                success=False,
                message=f"Request to Godot Editor timed out after {self.config.request_timeout}s.",
                mode=self.mode,
                error_code="TIMEOUT",
                actionable_hint="The Godot Editor might be blocked on a modal dialog or heavy computation.",
            )
        except (
            WebSocketException,
            OSError,
            json.JSONDecodeError,
        ) as e:
            return StandardResult(
                success=False,
                message=f"Could not connect to live Godot Editor on {self.uri}: {e!s}",
                mode=self.mode,
                error_code="DISCONNECTED",
                actionable_hint="Make sure Godot 4.7+ is running with the 'godot_mcp' plugin enabled in Project Settings -> Plugins.",
            )

    # --- LSP Overrides (Routed to Godot Language Server Protocol) ---

    async def query_lsp(
        self,
        file_path: str,
        query_type: str = "symbols",
        line: int = 1,
        character: int = 1,
        symbol_name: str | None = None,
    ) -> StandardResult:
        return await self.lsp.query(
            file_path=file_path,
            query_type=query_type,
            line=line,
            character=character,
            symbol_name=symbol_name,
        )

    async def rename_lsp_symbol(
        self,
        file_path: str,
        line: int,
        character: int,
        new_name: str,
    ) -> StandardResult:
        return await self.lsp.rename(
            file_path=file_path,
            line=line,
            character=character,
            new_name=new_name,
        )

    def __getattr__(self, name: str) -> Any:
        async def _dynamic_rpc(*args: Any, **kwargs: Any) -> StandardResult:
            return await self._send_rpc(name, kwargs)

        return _dynamic_rpc


# Dynamically bind all remaining GodotClient methods to RPC forwarders
for attr_name in dir(GodotClient):
    if not attr_name.startswith("_") and attr_name not in (
        "mode",
        "is_available",
        "query_lsp",
        "rename_lsp_symbol",
    ):
        attr = getattr(GodotClient, attr_name)
        if callable(attr):
            try:
                sig = inspect.signature(attr)
            except ValueError, TypeError:
                sig = None
            setattr(LiveBridgeClient, attr_name, _create_rpc_forwarder(attr_name, sig))

LiveBridgeClient.__abstractmethods__ = frozenset()
