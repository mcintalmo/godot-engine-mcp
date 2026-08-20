"""Live Editor Bridge client communicating with Godot EditorPlugin via WebSocket."""

import asyncio
import json
import logging
import uuid
from typing import Any

import websockets.exceptions
from websockets.legacy.client import connect

from godot_mcp.client.base import GodotClient
from godot_mcp.client.lsp_client import GodotLSPClient
from godot_mcp.config import GodotConfig
from godot_mcp.models.common import EngineMode, StandardResult

logger = logging.getLogger(__name__)


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
            websockets.exceptions.WebSocketException,
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

    async def set_tilemap_cells(
        self,
        node_path: str,
        cells: list[dict[str, Any]],
        clear_before_paint: bool = False,
    ) -> StandardResult:
        return await self._send_rpc(
            "set_tilemap_cells",
            {
                "node_path": node_path,
                "cells": cells,
                "clear_before_paint": clear_before_paint,
            },
        )

    async def get_tilemap_cells(
        self,
        node_path: str,
        region: list[int] | None = None,
    ) -> StandardResult:
        return await self._send_rpc(
            "get_tilemap_cells",
            {
                "node_path": node_path,
                "region": region or [],
            },
        )

    async def create_tilemap_layer(
        self,
        name: str = "TileMapLayer",
        parent_node_path: str = ".",
        tile_set_path: str | None = None,
    ) -> StandardResult:
        return await self._send_rpc(
            "create_tilemap_layer",
            {
                "name": name,
                "parent_node_path": parent_node_path,
                "tile_set_path": tile_set_path or "",
            },
        )

    async def bake_navmesh(
        self,
        node_path: str,
        dimension: str = "3D",
        on_thread: bool = True,
        agent_radius: float | None = None,
        agent_height: float | None = None,
        agent_max_climb: float | None = None,
        agent_max_slope: float | None = None,
        cell_size: float | None = None,
        cell_height: float | None = None,
        save_navmesh_path: str | None = None,
    ) -> StandardResult:
        return await self._send_rpc(
            "bake_navmesh",
            {
                "node_path": node_path,
                "dimension": dimension,
                "on_thread": on_thread,
                "agent_radius": agent_radius,
                "agent_height": agent_height,
                "agent_max_climb": agent_max_climb,
                "agent_max_slope": agent_max_slope,
                "cell_size": cell_size,
                "cell_height": cell_height,
                "save_navmesh_path": save_navmesh_path or "",
            },
        )

    async def create_navigation_region(
        self,
        name: str = "NavigationRegion3D",
        dimension: str = "3D",
        parent_node_path: str = ".",
        navmesh_path: str | None = None,
    ) -> StandardResult:
        return await self._send_rpc(
            "create_navigation_region",
            {
                "name": name,
                "dimension": dimension,
                "parent_node_path": parent_node_path,
                "navmesh_path": navmesh_path or "",
            },
        )

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

    async def get_performance_metrics(
        self,
        category: str = "all",
        include_custom_monitors: bool = True,
    ) -> StandardResult:
        return await self._send_rpc(
            "get_performance_metrics",
            {
                "category": category,
                "include_custom_monitors": include_custom_monitors,
            },
        )

    async def create_theme(
        self,
        save_path: str,
        base_font_path: str | None = None,
        base_font_size: int | None = None,
        colors: dict[str, dict[str, str]] | None = None,
        constants: dict[str, dict[str, int]] | None = None,
        styleboxes: dict[str, dict[str, Any]] | None = None,
        apply_to_node_path: str | None = None,
    ) -> StandardResult:
        return await self._send_rpc(
            "create_theme",
            {
                "save_path": save_path,
                "base_font_path": base_font_path or "",
                "base_font_size": base_font_size,
                "colors": colors or {},
                "constants": constants or {},
                "styleboxes": styleboxes or {},
                "apply_to_node_path": apply_to_node_path or "",
            },
        )

    async def apply_theme_override(
        self,
        node_path: str,
        override_type: str,
        item_name: str,
        value: Any,
    ) -> StandardResult:
        return await self._send_rpc(
            "apply_theme_override",
            {
                "node_path": node_path,
                "override_type": override_type,
                "item_name": item_name,
                "value": value,
            },
        )

    async def get_audio_layout(
        self,
        include_effects: bool = True,
    ) -> StandardResult:
        return await self._send_rpc(
            "get_audio_layout",
            {"include_effects": include_effects},
        )

    async def configure_audio_bus(
        self,
        bus_name: str,
        create_if_missing: bool = True,
        volume_db: float | None = None,
        volume_linear: float | None = None,
        send_to_bus: str | None = None,
        mute: bool | None = None,
        solo: bool | None = None,
        bypass_effects: bool | None = None,
        save_layout_path: str | None = None,
    ) -> StandardResult:
        return await self._send_rpc(
            "configure_audio_bus",
            {
                "bus_name": bus_name,
                "create_if_missing": create_if_missing,
                "volume_db": volume_db,
                "volume_linear": volume_linear,
                "send_to_bus": send_to_bus,
                "mute": mute,
                "solo": solo,
                "bypass_effects": bypass_effects,
                "save_layout_path": save_layout_path or "",
            },
        )

    async def set_bus_effect(
        self,
        bus_name: str,
        effect_type: str,
        effect_index: int | None = None,
        enabled: bool = True,
        properties: dict[str, Any] | None = None,
        save_layout_path: str | None = None,
    ) -> StandardResult:
        return await self._send_rpc(
            "set_bus_effect",
            {
                "bus_name": bus_name,
                "effect_type": effect_type,
                "effect_index": effect_index,
                "enabled": enabled,
                "properties": properties or {},
                "save_layout_path": save_layout_path or "",
            },
        )

    async def play_scene(
        self,
        mode: str = "main",
        custom_scene_path: str | None = None,
    ) -> StandardResult:
        return await self._send_rpc(
            "play_scene",
            {"mode": mode, "custom_scene_path": custom_scene_path or ""},
        )

    async def stop_scene(self) -> StandardResult:
        return await self._send_rpc("stop_scene", {})

    async def get_play_state(self) -> StandardResult:
        return await self._send_rpc("get_play_state", {})

    async def set_play_state(
        self,
        pause: bool | None = None,
        time_scale: float | None = None,
        step_frames: int | None = None,
    ) -> StandardResult:
        return await self._send_rpc(
            "set_play_state",
            {
                "pause": pause,
                "time_scale": time_scale,
                "step_frames": step_frames,
            },
        )

    async def cast_ray_3d(
        self,
        from_pos: tuple[float, float, float],
        to_pos: tuple[float, float, float],
        collision_mask: int = 0xFFFFFFFF,
        collide_with_bodies: bool = True,
        collide_with_areas: bool = False,
        hit_from_inside: bool = False,
        exclude_nodes: list[str] | None = None,
    ) -> StandardResult:
        return await self._send_rpc(
            "cast_ray_3d",
            {
                "from_pos": list(from_pos),
                "to_pos": list(to_pos),
                "collision_mask": collision_mask,
                "collide_with_bodies": collide_with_bodies,
                "collide_with_areas": collide_with_areas,
                "hit_from_inside": hit_from_inside,
                "exclude_nodes": exclude_nodes or [],
            },
        )

    async def cast_shape_3d(
        self,
        shape_type: str,
        shape_params: dict[str, float],
        origin: tuple[float, float, float],
        motion: tuple[float, float, float] | None = None,
        collision_mask: int = 0xFFFFFFFF,
        max_results: int = 32,
    ) -> StandardResult:
        return await self._send_rpc(
            "cast_shape_3d",
            {
                "shape_type": shape_type,
                "shape_params": shape_params,
                "origin": list(origin),
                "motion": list(motion) if motion is not None else None,
                "collision_mask": collision_mask,
                "max_results": max_results,
            },
        )

    async def get_body_physics_state_3d(
        self,
        node_path: str,
    ) -> StandardResult:
        return await self._send_rpc(
            "get_body_physics_state_3d",
            {"node_path": node_path},
        )

    async def set_physics_debug_mode(
        self,
        visible_collision_shapes: bool | None = None,
        visible_paths: bool | None = None,
        visible_navigation: bool | None = None,
        collision_debug_color: str | None = None,
    ) -> StandardResult:
        return await self._send_rpc(
            "set_physics_debug_mode",
            {
                "visible_collision_shapes": visible_collision_shapes,
                "visible_paths": visible_paths,
                "visible_navigation": visible_navigation,
                "collision_debug_color": collision_debug_color,
            },
        )
