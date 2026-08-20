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
        client = await self.get_active_client()
        return await client.create_theme(
            save_path=save_path,
            base_font_path=base_font_path,
            base_font_size=base_font_size,
            colors=colors,
            constants=constants,
            styleboxes=styleboxes,
            apply_to_node_path=apply_to_node_path,
        )

    async def apply_theme_override(
        self,
        node_path: str,
        override_type: str,
        item_name: str,
        value: Any,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.apply_theme_override(
            node_path=node_path,
            override_type=override_type,
            item_name=item_name,
            value=value,
        )

    async def get_audio_layout(
        self,
        include_effects: bool = True,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.get_audio_layout(
            include_effects=include_effects,
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
        client = await self.get_active_client()
        return await client.configure_audio_bus(
            bus_name=bus_name,
            create_if_missing=create_if_missing,
            volume_db=volume_db,
            volume_linear=volume_linear,
            send_to_bus=send_to_bus,
            mute=mute,
            solo=solo,
            bypass_effects=bypass_effects,
            save_layout_path=save_layout_path,
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
        client = await self.get_active_client()
        return await client.set_bus_effect(
            bus_name=bus_name,
            effect_type=effect_type,
            effect_index=effect_index,
            enabled=enabled,
            properties=properties,
            save_layout_path=save_layout_path,
        )

    async def play_scene(
        self,
        mode: str = "main",
        custom_scene_path: str | None = None,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.play_scene(
            mode=mode,
            custom_scene_path=custom_scene_path,
        )

    async def stop_scene(self) -> StandardResult:
        client = await self.get_active_client()
        return await client.stop_scene()

    async def get_play_state(self) -> StandardResult:
        client = await self.get_active_client()
        return await client.get_play_state()

    async def set_play_state(
        self,
        pause: bool | None = None,
        time_scale: float | None = None,
        step_frames: int | None = None,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.set_play_state(
            pause=pause,
            time_scale=time_scale,
            step_frames=step_frames,
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
        client = await self.get_active_client()
        return await client.cast_ray_3d(
            from_pos=from_pos,
            to_pos=to_pos,
            collision_mask=collision_mask,
            collide_with_bodies=collide_with_bodies,
            collide_with_areas=collide_with_areas,
            hit_from_inside=hit_from_inside,
            exclude_nodes=exclude_nodes,
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
        client = await self.get_active_client()
        return await client.cast_shape_3d(
            shape_type=shape_type,
            shape_params=shape_params,
            origin=origin,
            motion=motion,
            collision_mask=collision_mask,
            max_results=max_results,
        )

    async def get_body_physics_state_3d(
        self,
        node_path: str,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.get_body_physics_state_3d(
            node_path=node_path,
        )

    async def set_physics_debug_mode(
        self,
        visible_collision_shapes: bool | None = None,
        visible_paths: bool | None = None,
        visible_navigation: bool | None = None,
        collision_debug_color: str | None = None,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.set_physics_debug_mode(
            visible_collision_shapes=visible_collision_shapes,
            visible_paths=visible_paths,
            visible_navigation=visible_navigation,
            collision_debug_color=collision_debug_color,
        )

    async def get_input_actions(
        self,
        filter_prefix: str | None = None,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.get_input_actions(
            filter_prefix=filter_prefix,
        )

    async def configure_input_action(
        self,
        action_name: str,
        deadzone: float = 0.5,
        events: list[dict[str, Any]] | None = None,
        replace_existing: bool = True,
        save_to_project_settings: bool = True,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.configure_input_action(
            action_name=action_name,
            deadzone=deadzone,
            events=events,
            replace_existing=replace_existing,
            save_to_project_settings=save_to_project_settings,
        )

    async def configure_environment(
        self,
        save_path: str | None = None,
        node_path: str | None = None,
        background_mode: str | None = None,
        background_color: str | None = None,
        sky_type: str | None = None,
        sky_params: dict[str, Any] | None = None,
        ambient_light_source: str | None = None,
        ambient_light_color: str | None = None,
        ambient_light_energy: float | None = None,
        tonemap_mode: str | None = None,
        tonemap_exposure: float | None = None,
        glow_enabled: bool | None = None,
        glow_intensity: float | None = None,
        glow_bloom: float | None = None,
        glow_blend_mode: str | None = None,
        ssao_enabled: bool | None = None,
        ssao_radius: float | None = None,
        ssao_intensity: float | None = None,
        ssil_enabled: bool | None = None,
        ssr_enabled: bool | None = None,
        volumetric_fog_enabled: bool | None = None,
        volumetric_fog_density: float | None = None,
        volumetric_fog_albedo: str | None = None,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.configure_environment(
            save_path=save_path,
            node_path=node_path,
            background_mode=background_mode,
            background_color=background_color,
            sky_type=sky_type,
            sky_params=sky_params,
            ambient_light_source=ambient_light_source,
            ambient_light_color=ambient_light_color,
            ambient_light_energy=ambient_light_energy,
            tonemap_mode=tonemap_mode,
            tonemap_exposure=tonemap_exposure,
            glow_enabled=glow_enabled,
            glow_intensity=glow_intensity,
            glow_bloom=glow_bloom,
            glow_blend_mode=glow_blend_mode,
            ssao_enabled=ssao_enabled,
            ssao_radius=ssao_radius,
            ssao_intensity=ssao_intensity,
            ssil_enabled=ssil_enabled,
            ssr_enabled=ssr_enabled,
            volumetric_fog_enabled=volumetric_fog_enabled,
            volumetric_fog_density=volumetric_fog_density,
            volumetric_fog_albedo=volumetric_fog_albedo,
        )

    async def set_editor_selection(
        self,
        node_paths: list[str],
        clear_previous: bool = True,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.set_editor_selection(
            node_paths=node_paths,
            clear_previous=clear_previous,
        )

    async def focus_node(
        self,
        node_path: str,
        main_screen: str | None = None,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.focus_node(
            node_path=node_path,
            main_screen=main_screen,
        )
