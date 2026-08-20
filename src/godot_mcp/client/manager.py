"""Unified client manager coordinating Live Editor Bridge and Headless CLI fallback."""

from typing import Any

from godot_mcp.client.base import GodotClient
from godot_mcp.client.headless_cli import HeadlessCLIClient
from godot_mcp.client.live_bridge import LiveBridgeClient
from godot_mcp.config import GodotConfig
from godot_mcp.models.common import EngineMode, StandardResult


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

    async def get_version(self) -> StandardResult:
        client = await self.get_active_client()
        return await client.get_version()

    async def list_nodes(
        self,
        root_path: str = ".",
        max_depth: int = 4,
        include_properties: bool = False,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.list_nodes(root_path, max_depth, include_properties)

    async def get_node(
        self,
        node_path: str,
        include_inherited_properties: bool = False,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.get_node(node_path, include_inherited_properties)

    async def create_node(
        self,
        type_name: str,
        name: str,
        parent_path: str = ".",
        properties: dict[str, Any] | None = None,
        script_path: str | None = None,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.create_node(
            type_name, name, parent_path, properties, script_path
        )

    async def modify_node(
        self,
        node_path: str,
        properties: dict[str, Any],
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.modify_node(node_path, properties)

    async def delete_node(
        self,
        node_path: str,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.delete_node(node_path)

    async def connect_signal(
        self,
        source_node_path: str,
        signal_name: str,
        target_node_path: str,
        method_name: str,
        flags: int = 0,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.connect_signal(
            source_node_path, signal_name, target_node_path, method_name, flags
        )

    async def instantiate_scene(
        self,
        scene_path: str,
        parent_path: str = ".",
        name: str | None = None,
        properties: dict[str, Any] | None = None,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.instantiate_scene(scene_path, parent_path, name, properties)

    async def save_scene(
        self,
        scene_path: str | None = None,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.save_scene(scene_path)

    async def open_scene(
        self,
        scene_path: str,
    ) -> StandardResult:
        client = await self.get_active_client()
        if hasattr(client, "open_scene"):
            return await client.open_scene(scene_path)
        return StandardResult(
            success=False,
            message="Active client does not support opening scenes in editor.",
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
        client = await self.get_active_client()
        if hasattr(client, "create_scene"):
            return await client.create_scene(
                scene_path, root_type, root_name, properties, open_in_editor
            )
        return StandardResult(
            success=False,
            message="Active client does not support creating scenes.",
            mode=self.mode,
        )

    async def validate_script(
        self,
        script_path: str | None = None,
        code_content: str | None = None,
    ) -> StandardResult:
        # Script compilation diagnostics are always executed by the Godot CLI compiler
        return await self.headless_client.validate_script(script_path, code_content)

    async def validate_shader(
        self,
        shader_path: str | None = None,
        shader_code: str | None = None,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.validate_shader(shader_path, shader_code)

    async def create_material(
        self,
        material_path: str,
        material_type: str = "StandardMaterial3D",
        properties: dict[str, Any] | None = None,
        shader_path: str | None = None,
        shader_code: str | None = None,
        assign_to_node_path: str | None = None,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.create_material(
            material_path=material_path,
            material_type=material_type,
            properties=properties,
            shader_path=shader_path,
            shader_code=shader_code,
            assign_to_node_path=assign_to_node_path,
        )

    async def get_class_info(
        self,
        class_name: str,
        include_inherited: bool = True,
        category: str = "all",
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.get_class_info(class_name, include_inherited, category)

    async def get_documentation(
        self,
        query: str,
        category: str = "all",
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.get_documentation(query, category)

    async def create_script(
        self,
        path: str,
        content: str,
        inherits: str = "Node",
        attach_to_node: str | None = None,
    ) -> StandardResult:
        # Create file on disk
        result = await self.headless_client.create_script(
            path, content, inherits, attach_to_node
        )
        if result.success and attach_to_node and await self.live_client.is_available():
            # If live editor is running, also attach script property to node
            await self.live_client.modify_node(attach_to_node, {"script": path})
        return result

    async def get_project_settings(
        self,
        section: str | None = None,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.get_project_settings(section)

    async def set_project_setting(
        self,
        name: str,
        value: Any,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.set_project_setting(name, value)

    async def list_project_files(
        self,
        directory: str = "res://",
        extension_filter: list[str] | None = None,
        recursive: bool = True,
    ) -> StandardResult:
        # File listing operates on project filesystem
        return await self.headless_client.list_project_files(
            directory, extension_filter, recursive
        )

    async def run_project(
        self,
        scene_path: str | None = None,
        extra_arguments: list[str] | None = None,
        timeout_seconds: int = 10,
    ) -> StandardResult:
        return await self.headless_client.run_project(
            scene_path, extra_arguments, timeout_seconds
        )

    async def run_tests(
        self,
        test_path: str | None = None,
        extra_arguments: list[str] | None = None,
        timeout_seconds: int = 30,
    ) -> StandardResult:
        return await self.headless_client.run_tests(
            test_path, extra_arguments, timeout_seconds
        )

    async def take_screenshot(
        self,
        viewport_type: str = "main_2d_3d",
        output_path: str | None = None,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.take_screenshot(viewport_type, output_path)

    async def reimport_asset(
        self,
        asset_path: str,
        preset: str | None = None,
        custom_params: dict[str, Any] | None = None,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.reimport_asset(asset_path, preset, custom_params)

    async def create_collision_polygon(
        self,
        points: list[list[float]],
        polygon_type: str = "2D",
        parent_node_path: str = ".",
        node_name: str = "CollisionPolygon",
        depth: float = 1.0,
        disabled: bool = False,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.create_collision_polygon(
            points=points,
            polygon_type=polygon_type,
            parent_node_path=parent_node_path,
            node_name=node_name,
            depth=depth,
            disabled=disabled,
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
        client = await self.get_active_client()
        return await client.create_animation(
            animation_name=animation_name,
            length=length,
            loop_mode=loop_mode,
            step=step,
            tracks=tracks,
            animation_player_path=animation_player_path,
            save_path=save_path,
        )

    async def set_tilemap_cells(
        self,
        node_path: str,
        cells: list[dict[str, Any]],
        clear_before_paint: bool = False,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.set_tilemap_cells(node_path, cells, clear_before_paint)

    async def get_tilemap_cells(
        self,
        node_path: str,
        region: list[int] | None = None,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.get_tilemap_cells(node_path, region)

    async def create_tilemap_layer(
        self,
        name: str = "TileMapLayer",
        parent_node_path: str = ".",
        tile_set_path: str | None = None,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.create_tilemap_layer(name, parent_node_path, tile_set_path)

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
        client = await self.get_active_client()
        return await client.bake_navmesh(
            node_path=node_path,
            dimension=dimension,
            on_thread=on_thread,
            agent_radius=agent_radius,
            agent_height=agent_height,
            agent_max_climb=agent_max_climb,
            agent_max_slope=agent_max_slope,
            cell_size=cell_size,
            cell_height=cell_height,
            save_navmesh_path=save_navmesh_path,
        )

    async def create_navigation_region(
        self,
        name: str = "NavigationRegion3D",
        dimension: str = "3D",
        parent_node_path: str = ".",
        navmesh_path: str | None = None,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.create_navigation_region(
            name=name,
            dimension=dimension,
            parent_node_path=parent_node_path,
            navmesh_path=navmesh_path,
        )

    async def query_lsp(
        self,
        file_path: str,
        query_type: str = "symbols",
        line: int = 1,
        character: int = 1,
        symbol_name: str | None = None,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.query_lsp(
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
        client = await self.get_active_client()
        return await client.rename_lsp_symbol(
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
        client = await self.get_active_client()
        return await client.get_performance_metrics(
            category=category,
            include_custom_monitors=include_custom_monitors,
        )
