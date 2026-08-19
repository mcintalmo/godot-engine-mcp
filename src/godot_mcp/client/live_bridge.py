"""Live Editor Bridge client communicating with Godot EditorPlugin via WebSocket."""

import asyncio
import json
import logging
import uuid
from typing import Any

import websockets

from godot_mcp.client.base import GodotClient
from godot_mcp.config import GodotConfig
from godot_mcp.models.common import EngineMode, StandardResult

logger = logging.getLogger(__name__)


class LiveBridgeClient(GodotClient):
    """Client for communicating with the live Godot Editor via the godot_mcp addon."""

    def __init__(self, config: GodotConfig | None = None) -> None:
        self.config = config or GodotConfig.load()
        self.uri = f"ws://{self.config.bridge_host}:{self.config.bridge_port}/ws"

    @property
    def mode(self) -> EngineMode:
        return EngineMode.LIVE_EDITOR

    async def is_available(self) -> bool:
        """Check if the Godot Editor bridge server is responding."""
        try:
            async with asyncio.timeout(1.5):
                async with websockets.connect(self.uri, proxy=None) as ws:
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
            websockets.exceptions.WebSocketException,
            OSError,
            TimeoutError,
            json.JSONDecodeError,
            AttributeError,
        ):
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
                async with websockets.connect(self.uri, proxy=None) as ws:
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
            websockets.exceptions.WebSocketException,
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

    async def get_version(self) -> StandardResult:
        return await self._send_rpc("get_version")

    async def list_nodes(
        self,
        root_path: str = ".",
        max_depth: int = 4,
        include_properties: bool = False,
    ) -> StandardResult:
        return await self._send_rpc(
            "list_nodes",
            {
                "root_path": root_path,
                "max_depth": max_depth,
                "include_properties": include_properties,
            },
        )

    async def get_node(
        self,
        node_path: str,
        include_inherited_properties: bool = False,
    ) -> StandardResult:
        return await self._send_rpc(
            "get_node",
            {
                "node_path": node_path,
                "include_inherited_properties": include_inherited_properties,
            },
        )

    async def create_node(
        self,
        type_name: str,
        name: str,
        parent_path: str = ".",
        properties: dict[str, Any] | None = None,
        script_path: str | None = None,
    ) -> StandardResult:
        return await self._send_rpc(
            "create_node",
            {
                "type_name": type_name,
                "name": name,
                "parent_path": parent_path,
                "properties": properties or {},
                "script_path": script_path,
            },
        )

    async def modify_node(
        self,
        node_path: str,
        properties: dict[str, Any],
    ) -> StandardResult:
        return await self._send_rpc(
            "modify_node",
            {"node_path": node_path, "properties": properties},
        )

    async def delete_node(
        self,
        node_path: str,
    ) -> StandardResult:
        return await self._send_rpc("delete_node", {"node_path": node_path})

    async def connect_signal(
        self,
        source_node_path: str,
        signal_name: str,
        target_node_path: str,
        method_name: str,
        flags: int = 0,
    ) -> StandardResult:
        return await self._send_rpc(
            "connect_signal",
            {
                "source_node_path": source_node_path,
                "signal_name": signal_name,
                "target_node_path": target_node_path,
                "method_name": method_name,
                "flags": flags,
            },
        )

    async def instantiate_scene(
        self,
        scene_path: str,
        parent_path: str = ".",
        name: str | None = None,
        properties: dict[str, Any] | None = None,
    ) -> StandardResult:
        return await self._send_rpc(
            "instantiate_scene",
            {
                "scene_path": scene_path,
                "parent_path": parent_path,
                "name": name,
                "properties": properties or {},
            },
        )

    async def save_scene(
        self,
        scene_path: str | None = None,
    ) -> StandardResult:
        return await self._send_rpc("save_scene", {"scene_path": scene_path})

    async def validate_script(
        self,
        script_path: str | None = None,
        code_content: str | None = None,
    ) -> StandardResult:
        return await self._send_rpc(
            "validate_script",
            {"script_path": script_path, "code_content": code_content},
        )

    async def create_script(
        self,
        path: str,
        content: str,
        inherits: str = "Node",
        attach_to_node: str | None = None,
    ) -> StandardResult:
        return await self._send_rpc(
            "create_script",
            {
                "path": path,
                "content": content,
                "inherits": inherits,
                "attach_to_node": attach_to_node,
            },
        )

    async def get_project_settings(
        self,
        section: str | None = None,
    ) -> StandardResult:
        return await self._send_rpc("get_project_settings", {"section": section})

    async def set_project_setting(
        self,
        name: str,
        value: Any,
    ) -> StandardResult:
        return await self._send_rpc(
            "set_project_setting", {"name": name, "value": value}
        )

    async def list_project_files(
        self,
        directory: str = "res://",
        extension_filter: list[str] | None = None,
        recursive: bool = True,
    ) -> StandardResult:
        return await self._send_rpc(
            "list_project_files",
            {
                "directory": directory,
                "extension_filter": extension_filter or [],
                "recursive": recursive,
            },
        )

    async def run_project(
        self,
        scene_path: str | None = None,
        extra_arguments: list[str] | None = None,
        timeout_seconds: int = 10,
    ) -> StandardResult:
        return await self._send_rpc(
            "run_project",
            {
                "scene_path": scene_path,
                "extra_arguments": extra_arguments or [],
                "timeout_seconds": timeout_seconds,
            },
        )

    async def run_tests(
        self,
        test_path: str | None = None,
        extra_arguments: list[str] | None = None,
        timeout_seconds: int = 30,
    ) -> StandardResult:
        return await self._send_rpc(
            "run_tests",
            {
                "test_path": test_path,
                "extra_arguments": extra_arguments or [],
                "timeout_seconds": timeout_seconds,
            },
        )

    async def open_scene(self, scene_path: str) -> StandardResult:
        return await self._send_rpc("open_scene", {"scene_path": scene_path})

    async def create_scene(
        self,
        scene_path: str,
        root_type: str = "Node2D",
        root_name: str = "Root",
        properties: dict[str, Any] | None = None,
        open_in_editor: bool = True,
    ) -> StandardResult:
        return await self._send_rpc(
            "create_scene",
            {
                "scene_path": scene_path,
                "root_type": root_type,
                "root_name": root_name,
                "properties": properties or {},
                "open_in_editor": open_in_editor,
            },
        )

    async def take_screenshot(
        self,
        viewport_type: str = "main_2d_3d",
        output_path: str | None = None,
    ) -> StandardResult:
        return await self._send_rpc(
            "take_screenshot",
            {"viewport_type": viewport_type, "output_path": output_path},
        )

    async def get_class_info(
        self,
        class_name: str,
        include_inherited: bool = True,
        category: str = "all",
    ) -> StandardResult:
        return await self._send_rpc(
            "get_class_info",
            {
                "class_name": class_name,
                "include_inherited": include_inherited,
                "category": category,
            },
        )

    async def get_documentation(
        self,
        query: str,
        category: str = "all",
    ) -> StandardResult:
        return await self._send_rpc(
            "get_documentation",
            {"query": query, "category": category},
        )

    async def validate_shader(
        self,
        shader_path: str | None = None,
        shader_code: str | None = None,
    ) -> StandardResult:
        return await self._send_rpc(
            "validate_shader",
            {"shader_path": shader_path, "shader_code": shader_code},
        )

    async def create_material(
        self,
        material_path: str,
        material_type: str = "StandardMaterial3D",
        properties: dict[str, Any] | None = None,
        shader_path: str | None = None,
        shader_code: str | None = None,
        assign_to_node_path: str | None = None,
    ) -> StandardResult:
        return await self._send_rpc(
            "create_material",
            {
                "material_path": material_path,
                "material_type": material_type,
                "properties": properties or {},
                "shader_path": shader_path or "",
                "shader_code": shader_code or "",
                "assign_to_node_path": assign_to_node_path or "",
            },
        )

    async def reimport_asset(
        self,
        asset_path: str,
        preset: str | None = None,
        custom_params: dict[str, Any] | None = None,
    ) -> StandardResult:
        return await self._send_rpc(
            "reimport_asset",
            {
                "asset_path": asset_path,
                "preset": preset or "",
                "custom_params": custom_params or {},
            },
        )

    async def create_collision_polygon(
        self,
        points: list[list[float]],
        polygon_type: str = "2D",
        parent_node_path: str = ".",
        node_name: str = "CollisionPolygon",
        depth: float = 1.0,
        disabled: bool = False,
    ) -> StandardResult:
        return await self._send_rpc(
            "create_collision_polygon",
            {
                "points": points,
                "polygon_type": polygon_type,
                "parent_node_path": parent_node_path,
                "node_name": node_name,
                "depth": depth,
                "disabled": disabled,
            },
        )

    async def create_animation(
        self,
        animation_name: str,
        length: float = 1.0,
        loop_mode: str = "none",
        step: float = 0.1,
        tracks: list[dict[str, Any]] | None = None,
        animation_player_path: str | None = None,
        save_path: str | None = None,
    ) -> StandardResult:
        return await self._send_rpc(
            "create_animation",
            {
                "animation_name": animation_name,
                "length": length,
                "loop_mode": loop_mode,
                "step": step,
                "tracks": tracks or [],
                "animation_player_path": animation_player_path or "",
                "save_path": save_path or "",
            },
        )
