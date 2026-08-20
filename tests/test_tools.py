"""Unit tests for all tool handlers with MockGodotClient."""

from typing import Any

import pytest

from godot_mcp.client.base import GodotClient
from godot_mcp.models.common import EngineMode, ResponseFormat, StandardResult
from godot_mcp.models.debug import (
    RunProjectInput,
    RunTestsInput,
    TakeScreenshotInput,
)
from godot_mcp.models.material import CreateMaterialInput, MaterialType
from godot_mcp.models.project import (
    GetProjectSettingsInput,
    GetVersionInput,
    ListProjectFilesInput,
    SetProjectSettingInput,
)
from godot_mcp.models.reflection import (
    GetClassInfoInput,
    GetDocumentationInput,
    ValidateShaderInput,
)
from godot_mcp.models.scene import (
    ConnectSignalInput,
    CreateNodeInput,
    CreateSceneInput,
    DeleteNodeInput,
    GetNodeInput,
    InstantiateSceneInput,
    ListNodesInput,
    ModifyNodeInput,
    OpenSceneInput,
    SaveSceneInput,
)
from godot_mcp.models.script import (
    CreateScriptInput,
    ValidateScriptInput,
)
from godot_mcp.tools.debug_tools import (
    handle_run_project,
    handle_run_tests,
    handle_take_screenshot,
)
from godot_mcp.tools.material_tools import handle_create_material
from godot_mcp.tools.project_tools import (
    handle_get_project_settings,
    handle_get_version,
    handle_list_project_files,
    handle_set_project_setting,
)
from godot_mcp.tools.reflection_tools import (
    handle_get_class_info,
    handle_get_documentation,
    handle_validate_shader,
)
from godot_mcp.tools.scene_tools import (
    handle_connect_signal,
    handle_create_node,
    handle_create_scene,
    handle_delete_node,
    handle_get_node,
    handle_instantiate_scene,
    handle_list_nodes,
    handle_modify_node,
    handle_open_scene,
    handle_save_scene,
)
from godot_mcp.tools.script_tools import (
    handle_create_script,
    handle_validate_script,
)


class MockGodotClient(GodotClient):
    """Mock client returning standard results for tool handler testing."""

    @property
    def mode(self) -> EngineMode:
        return EngineMode.LIVE_EDITOR

    async def is_available(self) -> bool:
        return True

    async def get_version(self) -> StandardResult:
        return StandardResult(
            success=True,
            message="Godot 4.7.1",
            mode=self.mode,
            data={"version_string": "4.7.1.stable", "major": 4, "minor": 7, "patch": 1},
        )

    async def list_nodes(
        self,
        root_path: str = ".",
        max_depth: int = 4,
        include_properties: bool = False,
    ) -> StandardResult:
        return StandardResult(
            success=True,
            message="Found 2 nodes",
            mode=self.mode,
            data={
                "nodes": [
                    {"name": "Root", "node_path": ".", "type_name": "Node2D"},
                    {
                        "name": "Sprite2D",
                        "node_path": "Sprite2D",
                        "type_name": "Sprite2D",
                    },
                ]
            },
        )

    async def get_node(
        self,
        node_path: str,
        include_inherited_properties: bool = False,
    ) -> StandardResult:
        return StandardResult(
            success=True,
            message=f"Node {node_path}",
            mode=self.mode,
            data={"node": {"name": "Sprite2D", "type_name": "Sprite2D"}},
        )

    async def create_node(
        self,
        type_name: str,
        name: str,
        parent_path: str = ".",
        properties: dict[str, Any] | None = None,
        script_path: str | None = None,
    ) -> StandardResult:
        return StandardResult(
            success=True,
            message=f"Created {name}",
            mode=self.mode,
            data={"node_path": f"{parent_path}/{name}".replace("./", "")},
        )

    async def modify_node(
        self,
        node_path: str,
        properties: dict[str, Any],
    ) -> StandardResult:
        return StandardResult(
            success=True,
            message=f"Modified {node_path}",
            mode=self.mode,
            data={"node_path": node_path, "properties": properties},
        )

    async def delete_node(
        self,
        node_path: str,
    ) -> StandardResult:
        return StandardResult(
            success=True,
            message=f"Deleted {node_path}",
            mode=self.mode,
        )

    async def connect_signal(
        self,
        source_node_path: str,
        signal_name: str,
        target_node_path: str,
        method_name: str,
        flags: int = 0,
    ) -> StandardResult:
        return StandardResult(
            success=True,
            message=f"Connected {signal_name}",
            mode=self.mode,
        )

    async def instantiate_scene(
        self,
        scene_path: str,
        parent_path: str = ".",
        name: str | None = None,
        properties: dict[str, Any] | None = None,
    ) -> StandardResult:
        return StandardResult(
            success=True,
            message=f"Instantiated {scene_path}",
            mode=self.mode,
            data={"node_path": "InstancedScene"},
        )

    async def save_scene(
        self,
        scene_path: str | None = None,
    ) -> StandardResult:
        return StandardResult(
            success=True,
            message="Saved scene",
            mode=self.mode,
        )

    async def open_scene(
        self,
        scene_path: str,
    ) -> StandardResult:
        return StandardResult(
            success=True,
            message=f"Opened scene {scene_path}",
            mode=self.mode,
        )

    async def create_scene(
        self,
        scene_path: str,
        root_type: str = "Node2D",
        root_name: str = "Root",
        properties: dict[str, Any] | None = None,
        open_in_editor: bool = True,
    ) -> StandardResult:
        return StandardResult(
            success=True,
            message=f"Created new scene {scene_path} with root node {root_name}",
            mode=self.mode,
        )

    async def validate_script(
        self,
        script_path: str | None = None,
        code_content: str | None = None,
    ) -> StandardResult:
        return StandardResult(
            success=True,
            message="Script valid",
            mode=self.mode,
            data={"valid": True},
        )

    async def validate_shader(
        self,
        shader_path: str | None = None,
        shader_code: str | None = None,
    ) -> StandardResult:
        return StandardResult(
            success=True,
            message="Shader valid",
            mode=self.mode,
            data={"valid": True},
        )

    async def get_class_info(
        self,
        class_name: str,
        include_inherited: bool = True,
        category: str = "all",
    ) -> StandardResult:
        return StandardResult(
            success=True,
            message=f"ClassDB metadata for {class_name}",
            mode=self.mode,
            data={
                "class_name": class_name,
                "inherits": "Node",
                "is_instantiable": True,
                "properties": [{"name": "velocity", "type": "Vector2"}],
                "methods": [
                    {"name": "move_and_slide", "args": [], "return_type": "bool"}
                ],
                "signals": [{"name": "tree_entered", "args": []}],
                "enums": {"ProcessMode": {"PROCESS_MODE_INHERIT": 0}},
                "constants": {"NOTIFICATION_ENTER_TREE": 10},
            },
        )

    async def get_documentation(
        self,
        query: str,
        category: str = "all",
    ) -> StandardResult:
        return StandardResult(
            success=True,
            message=f"Documentation for {query}",
            mode=self.mode,
            data={
                "class_name": query,
                "description": f"Documentation summary for {query}",
            },
        )

    async def create_script(
        self,
        path: str,
        content: str,
        inherits: str = "Node",
        attach_to_node: str | None = None,
    ) -> StandardResult:
        return StandardResult(
            success=True,
            message=f"Created {path}",
            mode=self.mode,
        )

    async def get_project_settings(
        self,
        section: str | None = None,
    ) -> StandardResult:
        return StandardResult(
            success=True,
            message="Settings retrieved",
            mode=self.mode,
            data={"settings": {"application/config/name": "MyGame"}},
        )

    async def set_project_setting(
        self,
        name: str,
        value: Any,
    ) -> StandardResult:
        return StandardResult(
            success=True,
            message=f"Set {name}",
            mode=self.mode,
        )

    async def list_project_files(
        self,
        directory: str = "res://",
        extension_filter: list[str] | None = None,
        recursive: bool = True,
    ) -> StandardResult:
        return StandardResult(
            success=True,
            message="Files found",
            mode=self.mode,
            data={
                "files": [
                    {
                        "path": "res://main.tscn",
                        "type_name": "PackedScene",
                        "size_bytes": 100,
                    }
                ]
            },
        )

    async def run_project(
        self,
        scene_path: str | None = None,
        extra_arguments: list[str] | None = None,
        timeout_seconds: int = 10,
    ) -> StandardResult:
        return StandardResult(
            success=True,
            message="Project ran",
            mode=self.mode,
            data={"status": "completed"},
        )

    async def run_tests(
        self,
        test_path: str | None = None,
        extra_arguments: list[str] | None = None,
        timeout_seconds: int = 30,
    ) -> StandardResult:
        return StandardResult(
            success=True,
            message="All tests passed",
            mode=self.mode,
            data={"returncode": 0},
        )

    async def take_screenshot(
        self,
        viewport_type: str = "main_2d_3d",
        output_path: str | None = None,
    ) -> StandardResult:
        return StandardResult(
            success=True,
            message="Screenshot taken",
            mode=self.mode,
            data={"width": 1920, "height": 1080},
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
        return StandardResult(
            success=True,
            message=f"Created material {material_path} of type {material_type}",
            mode=self.mode,
            data={
                "material_path": material_path,
                "material_type": material_type,
                "properties_applied": properties or {},
                "assigned_to_node": assign_to_node_path or "",
            },
        )

    async def reimport_asset(
        self,
        asset_path: str,
        preset: str | None = None,
        custom_params: dict[str, Any] | None = None,
    ) -> StandardResult:
        return StandardResult(
            success=True,
            message=f"Reimported asset {asset_path}",
            mode=self.mode,
            data={
                "asset_path": asset_path,
                "preset_applied": preset or "custom",
                "parameters_updated": custom_params or {},
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
        return StandardResult(
            success=True,
            message=f"Created {polygon_type} collision polygon {node_name}",
            mode=self.mode,
            data={
                "node_name": node_name,
                "polygon_type": polygon_type,
                "vertex_count": len(points),
                "depth": depth if polygon_type == "3D" else None,
                "parent_node_path": parent_node_path,
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
        return StandardResult(
            success=True,
            message=f"Created animation '{animation_name}'",
            mode=self.mode,
            data={
                "animation_name": animation_name,
                "length": length,
                "loop_mode": loop_mode,
                "step": step,
                "track_count": len(tracks or []),
                "keyframe_count": sum(
                    len(t.get("keyframes", [])) for t in (tracks or [])
                ),
                "attached_to_animation_player": animation_player_path or "",
                "saved_to_file": save_path or "",
            },
        )

    async def set_tilemap_cells(
        self,
        node_path: str,
        cells: list[dict[str, Any]],
        clear_before_paint: bool = False,
    ) -> StandardResult:

        erased = sum(1 for c in cells if c.get("source_id") == -1)
        painted = len(cells) - erased
        return StandardResult(
            success=True,
            message=f"Applied tile cells to '{node_path}'",
            mode=self.mode,
            data={
                "node_path": node_path,
                "node_name": node_path.split("/")[-1],
                "painted_count": painted,
                "erased_count": erased,
                "used_rect": [0, 0, 10, 10],
            },
        )

    async def get_tilemap_cells(
        self,
        node_path: str,
        region: list[int] | None = None,
    ) -> StandardResult:
        return StandardResult(
            success=True,
            message=f"Retrieved 2 cells from '{node_path}'",
            mode=self.mode,
            data={
                "node_path": node_path,
                "node_name": node_path.split("/")[-1],
                "cell_count": 2,
                "cells": [
                    {
                        "coords": [0, 0],
                        "source_id": 0,
                        "atlas_coords": [0, 0],
                        "alternative_tile": 0,
                    },
                    {
                        "coords": [1, 0],
                        "source_id": 0,
                        "atlas_coords": [1, 0],
                        "alternative_tile": 0,
                    },
                ],
                "used_rect": [0, 0, 2, 1],
            },
        )

    async def create_tilemap_layer(
        self,
        name: str = "TileMapLayer",
        parent_node_path: str = ".",
        tile_set_path: str | None = None,
    ) -> StandardResult:
        return StandardResult(
            success=True,
            message=f"Created TileMapLayer '{name}'",
            mode=self.mode,
            data={
                "node_name": name,
                "type_name": "TileMapLayer",
                "parent_node_path": parent_node_path,
                "tile_set_attached": tile_set_path,
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
        params: dict[str, Any] = {}
        if agent_radius is not None:
            params["agent_radius"] = agent_radius
        if agent_height is not None and dimension == "3D":
            params["agent_height"] = agent_height
        if agent_max_climb is not None and dimension == "3D":
            params["agent_max_climb"] = agent_max_climb
        if agent_max_slope is not None and dimension == "3D":
            params["agent_max_slope"] = agent_max_slope
        if cell_size is not None:
            params["cell_size"] = cell_size
        if cell_height is not None and dimension == "3D":
            params["cell_height"] = cell_height

        return StandardResult(
            success=True,
            message=f"Triggered {dimension} navigation mesh baking for '{node_path}'",
            mode=self.mode,
            data={
                "node_name": node_path.split("/")[-1],
                "dimension": dimension,
                "on_thread": on_thread,
                "parameters": params,
                "saved_to_file": save_navmesh_path,
            },
        )

    async def create_navigation_region(
        self,
        name: str = "NavigationRegion3D",
        dimension: str = "3D",
        parent_node_path: str = ".",
        navmesh_path: str | None = None,
    ) -> StandardResult:
        type_name = "NavigationRegion3D" if dimension == "3D" else "NavigationRegion2D"
        return StandardResult(
            success=True,
            message=f"Created {type_name} '{name}'",
            mode=self.mode,
            data={
                "node_name": name,
                "type_name": type_name,
                "dimension": dimension,
                "parent_node_path": parent_node_path,
                "navmesh_attached": navmesh_path if navmesh_path else "default",
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
        if query_type == "symbols":
            return StandardResult(
                success=True,
                message=f"Found 2 symbols in '{file_path}'",
                mode=self.mode,
                data={
                    "file_path": file_path,
                    "query_type": query_type,
                    "symbols": [
                        {
                            "name": "speed",
                            "kind": "Variable",
                            "line": 5,
                            "signature": "var speed: float = 200.0",
                        },
                        {
                            "name": "_ready",
                            "kind": "Function",
                            "line": 8,
                            "signature": "func _ready() -> void",
                        },
                    ],
                },
            )
        elif query_type == "definition":
            return StandardResult(
                success=True,
                message=f"Found definition for 'speed' at {file_path}:5",
                mode=self.mode,
                data={
                    "file_path": file_path,
                    "query_type": query_type,
                    "symbol": "speed",
                    "definition": {
                        "file": file_path,
                        "line": 5,
                        "line_content": "var speed: float = 200.0",
                    },
                },
            )
        elif query_type == "references":
            return StandardResult(
                success=True,
                message="Found 2 references to 'speed'",
                mode=self.mode,
                data={
                    "file_path": file_path,
                    "query_type": query_type,
                    "symbol": "speed",
                    "references": [
                        {
                            "file": file_path,
                            "line": 5,
                            "line_content": "var speed: float = 200.0",
                        },
                        {
                            "file": file_path,
                            "line": 12,
                            "line_content": "position += velocity * speed * delta",
                        },
                    ],
                },
            )
        elif query_type == "hover":
            return StandardResult(
                success=True,
                message="Hover info for 'speed'",
                mode=self.mode,
                data={
                    "file_path": file_path,
                    "query_type": query_type,
                    "hover": {
                        "symbol": "speed",
                        "signature": "var speed: float = 200.0",
                        "docstring": "Movement speed in pixels per second.",
                    },
                },
            )
        return StandardResult(
            success=False,
            message=f"Unknown query_type: {query_type}",
            mode=self.mode,
        )

    async def rename_lsp_symbol(
        self,
        file_path: str,
        line: int,
        character: int,
        new_name: str,
    ) -> StandardResult:
        return StandardResult(
            success=True,
            message=f"Renamed symbol 'speed' -> '{new_name}' across 1 files.",
            mode=self.mode,
            data={
                "old_name": "speed",
                "new_name": new_name,
                "modified_files": [file_path],
            },
        )

    async def get_performance_metrics(
        self,
        category: str = "all",
        include_custom_monitors: bool = True,
    ) -> StandardResult:
        data: dict[str, Any] = {
            "category": category,
            "time": {
                "fps": 60,
                "process_time_ms": 16.67,
                "physics_process_time_ms": 16.67,
                "navigation_process_time_ms": 0.5,
            },
            "render": {
                "draw_calls_in_frame": 42,
                "objects_in_frame": 120,
                "primitives_in_frame": 5400,
                "video_mem_mb": 18.5,
                "texture_mem_mb": 12.0,
                "buffer_mem_mb": 6.5,
            },
            "memory": {
                "static_ram_mb": 34.2,
                "static_ram_peak_mb": 45.0,
                "message_buffer_kb": 128.0,
            },
            "objects": {
                "node_count": 25,
                "resource_count": 80,
                "object_count": 310,
                "orphan_node_count": 0,
            },
        }
        if include_custom_monitors:
            data["custom"] = {"active_enemies": 5}

        return StandardResult(
            success=True,
            message="Engine Telemetry: 60 FPS, 42 Draw Calls",
            mode=self.mode,
            data=data,
        )


@pytest.mark.asyncio
async def test_all_scene_tools() -> None:
    """Test all scene tool handlers."""
    client = MockGodotClient()

    res = await handle_list_nodes(client, ListNodesInput())
    assert "Found 2 nodes" in res

    res = await handle_get_node(client, GetNodeInput(node_path="Sprite2D"))
    assert "Node Sprite2D" in res

    res = await handle_create_node(
        client, CreateNodeInput(type_name="Sprite2D", name="Hero")
    )
    assert "Created Hero" in res

    res = await handle_modify_node(
        client, ModifyNodeInput(node_path="Hero", properties={"visible": True})
    )
    assert "Modified Hero" in res

    res = await handle_delete_node(client, DeleteNodeInput(node_path="Hero"))
    assert "Deleted Hero" in res

    res = await handle_connect_signal(
        client,
        ConnectSignalInput(
            source_node_path="Btn",
            signal_name="pressed",
            target_node_path=".",
            method_name="_on_click",
        ),
    )
    assert "Connected pressed" in res

    res = await handle_instantiate_scene(
        client, InstantiateSceneInput(scene_path="res://player.tscn")
    )
    assert "Instantiated res://player.tscn" in res

    res = await handle_save_scene(client, SaveSceneInput())
    assert "Saved scene" in res

    res = await handle_open_scene(
        client, OpenSceneInput(scene_path="res://scenes/main.tscn")
    )
    assert "Opened scene res://scenes/main.tscn" in res

    res = await handle_create_scene(
        client,
        CreateSceneInput(
            scene_path="res://scenes/new_gui.tscn",
            root_type="Control",
            root_name="NewGUI",
        ),
    )
    assert "Created new scene res://scenes/new_gui.tscn" in res


@pytest.mark.asyncio
async def test_all_project_and_debug_tools() -> None:
    """Test project, script, and debug tool handlers."""
    client = MockGodotClient()

    res = await handle_get_version(
        client, GetVersionInput(response_format=ResponseFormat.JSON)
    )
    assert '"major": 4' in res

    res = await handle_get_project_settings(client, GetProjectSettingsInput())
    assert "application/config/name" in res

    res = await handle_set_project_setting(
        client, SetProjectSettingInput(name="app/name", value="Test")
    )
    assert "Set app/name" in res

    res = await handle_list_project_files(client, ListProjectFilesInput())
    assert "res://main.tscn" in res

    res = await handle_validate_script(
        client, ValidateScriptInput(code_content="extends Node")
    )
    assert "Script valid" in res

    res = await handle_create_script(
        client, CreateScriptInput(path="res://test.gd", content="pass")
    )
    assert "Created res://test.gd" in res

    res = await handle_run_project(client, RunProjectInput())
    assert "Project ran" in res

    res = await handle_run_tests(client, RunTestsInput())
    assert "All tests passed" in res

    res = await handle_take_screenshot(client, TakeScreenshotInput())
    assert "Screenshot taken" in res

    res = await handle_validate_shader(
        client, ValidateShaderInput(shader_code="shader_type canvas_item;")
    )
    assert "Shader valid" in res

    res = await handle_get_class_info(
        client, GetClassInfoInput(class_name="CharacterBody2D")
    )
    assert "Class `CharacterBody2D`" in res

    res = await handle_get_documentation(
        client, GetDocumentationInput(query="CharacterBody2D.move_and_slide")
    )
    assert "Documentation for CharacterBody2D.move_and_slide" in res

    res = await handle_create_material(
        client,
        CreateMaterialInput(
            material_path="res://materials/neon.tres",
            material_type=MaterialType.STANDARD_3D,
            properties={"albedo_color": [0.2, 0.8, 1.0, 1.0]},
        ),
    )
    assert "Created material res://materials/neon.tres" in res
