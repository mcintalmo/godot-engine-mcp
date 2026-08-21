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
        disconnect: bool = False,
        persist: bool = True,
        one_shot: bool = False,
        deferred: bool = False,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.connect_signal(
            source_node_path=source_node_path,
            signal_name=signal_name,
            target_node_path=target_node_path,
            method_name=method_name,
            disconnect=disconnect,
            persist=persist,
            one_shot=one_shot,
            deferred=deferred,
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

    async def instantiate_model(
        self,
        source_path: str,
        parent_path: str | None = None,
        node_name: str | None = None,
        position: tuple[float, float, float] | None = None,
        rotation: tuple[float, float, float] | None = None,
        scale: tuple[float, float, float] | None = None,
        collision_mode: str = "none",
        save_as_scene_path: str | None = None,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.instantiate_model(
            source_path=source_path,
            parent_path=parent_path,
            node_name=node_name,
            position=position,
            rotation=rotation,
            scale=scale,
            collision_mode=collision_mode,
            save_as_scene_path=save_as_scene_path,
        )

    async def configure_gltf_import(
        self,
        model_path: str,
        import_as_skeleton_bones: bool | None = None,
        generate_lods: bool | None = None,
        lod_threshold: float | None = None,
        generate_shadow_mesh: bool | None = None,
        extract_materials: bool | None = None,
        reimport: bool = True,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.configure_gltf_import(
            model_path=model_path,
            import_as_skeleton_bones=import_as_skeleton_bones,
            generate_lods=generate_lods,
            lod_threshold=lod_threshold,
            generate_shadow_mesh=generate_shadow_mesh,
            extract_materials=extract_materials,
            reimport=reimport,
        )

    async def configure_particles(
        self,
        node_path: str | None = None,
        parent_path: str | None = None,
        node_name: str | None = None,
        save_path: str | None = None,
        particle_type: str = "gpu_3d",
        amount: int = 64,
        lifetime: float = 1.0,
        explosiveness: float = 0.0,
        emission_shape: str = "point",
        emission_sphere_radius: float | None = None,
        emission_box_extents: tuple[float, float, float] | None = None,
        direction: tuple[float, float, float] = (0.0, 1.0, 0.0),
        spread: float = 45.0,
        initial_velocity_min: float = 2.0,
        initial_velocity_max: float = 5.0,
        gravity: tuple[float, float, float] = (0.0, -9.8, 0.0),
        color_gradient: list[str] | None = None,
        scale_min: float = 1.0,
        scale_max: float = 1.0,
        emitting: bool = True,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.configure_particles(
            node_path=node_path,
            parent_path=parent_path,
            node_name=node_name,
            save_path=save_path,
            particle_type=particle_type,
            amount=amount,
            lifetime=lifetime,
            explosiveness=explosiveness,
            emission_shape=emission_shape,
            emission_sphere_radius=emission_sphere_radius,
            emission_box_extents=emission_box_extents,
            direction=direction,
            spread=spread,
            initial_velocity_min=initial_velocity_min,
            initial_velocity_max=initial_velocity_max,
            gravity=gravity,
            color_gradient=color_gradient,
            scale_min=scale_min,
            scale_max=scale_max,
            emitting=emitting,
        )

    async def get_export_presets(self) -> StandardResult:
        client = await self.get_active_client()
        return await client.get_export_presets()

    async def export_project(
        self,
        preset_name: str,
        output_path: str,
        debug: bool = False,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.export_project(
            preset_name=preset_name,
            output_path=output_path,
            debug=debug,
        )

    async def get_autoloads(self) -> StandardResult:
        client = await self.get_active_client()
        return await client.get_autoloads()

    async def set_autoload(
        self,
        name: str,
        path: str | None = None,
        is_singleton: bool = True,
        remove: bool = False,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.set_autoload(
            name=name,
            path=path,
            is_singleton=is_singleton,
            remove=remove,
        )

    async def get_node_signals(
        self,
        node_path: str,
        include_inherited: bool = True,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.get_node_signals(
            node_path=node_path,
            include_inherited=include_inherited,
        )

    async def get_signal_connections(
        self,
        node_path: str,
        signal_name: str | None = None,
        incoming: bool = True,
        outgoing: bool = True,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.get_signal_connections(
            node_path=node_path,
            signal_name=signal_name,
            incoming=incoming,
            outgoing=outgoing,
        )

    async def evaluate_expression(
        self,
        expression: str,
        node_path: str | None = None,
        input_variables: dict[str, Any] | None = None,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.evaluate_expression(
            expression=expression,
            node_path=node_path,
            input_variables=input_variables,
        )

    async def create_shader(
        self,
        path: str,
        shader_type: str = "spatial",
        code: str | None = None,
        create_material: bool = True,
        material_save_path: str | None = None,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.create_shader(
            path=path,
            shader_type=shader_type,
            code=code,
            create_material=create_material,
            material_save_path=material_save_path,
        )

    async def set_shader_param(
        self,
        parameter_name: str,
        value: Any,
        node_path: str | None = None,
        material_path: str | None = None,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.set_shader_param(
            parameter_name=parameter_name,
            value=value,
            node_path=node_path,
            material_path=material_path,
        )

    async def configure_animation_tree(
        self,
        node_path: str | None = None,
        parent_path: str | None = None,
        node_name: str = "AnimationTree",
        anim_player_path: str | None = None,
        tree_type: str = "state_machine",
        active: bool = True,
        states: list[dict[str, Any]] | None = None,
        transitions: list[dict[str, Any]] | None = None,
        save_as_resource_path: str | None = None,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.configure_animation_tree(
            node_path=node_path,
            parent_path=parent_path,
            node_name=node_name,
            anim_player_path=anim_player_path,
            tree_type=tree_type,
            active=active,
            states=states,
            transitions=transitions,
            save_as_resource_path=save_as_resource_path,
        )

    async def get_translations(
        self,
        locale_filter: str | None = None,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.get_translations(locale_filter=locale_filter)

    async def add_translation(
        self,
        translation_path: str,
        test_locale: str | None = None,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.add_translation(
            translation_path=translation_path,
            test_locale=test_locale,
        )

    async def get_uid(
        self,
        path: str,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.get_uid(path=path)

    async def resolve_uid(
        self,
        uid: str,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.resolve_uid(uid=uid)

    async def get_dependencies(
        self,
        path: str,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.get_dependencies(path=path)

    async def get_plugins(
        self,
        enabled_only: bool = False,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.get_plugins(enabled_only=enabled_only)

    async def set_plugin_status(
        self,
        plugin_name: str,
        enabled: bool = True,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.set_plugin_status(
            plugin_name=plugin_name,
            enabled=enabled,
        )

    async def configure_navigation_obstacle(
        self,
        node_path: str | None = None,
        parent_path: str | None = None,
        node_name: str = "NavigationObstacle3D",
        is_3d: bool = True,
        radius: float = 1.0,
        velocity: list[float] | None = None,
        vertices: list[list[float]] | None = None,
        avoidance_layers: int = 1,
        affect_navigation_mesh: bool = False,
        carve_navigation_mesh: bool = False,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.configure_navigation_obstacle(
            node_path=node_path,
            parent_path=parent_path,
            node_name=node_name,
            is_3d=is_3d,
            radius=radius,
            velocity=velocity,
            vertices=vertices,
            avoidance_layers=avoidance_layers,
            affect_navigation_mesh=affect_navigation_mesh,
            carve_navigation_mesh=carve_navigation_mesh,
        )

    async def configure_tileset_terrain(
        self,
        tileset_path: str,
        terrain_set: int = 0,
        mode: str = "match_corners_and_sides",
        terrains: list[dict[str, Any]] | None = None,
        tile_peering_bits: list[dict[str, Any]] | None = None,
        save_path: str | None = None,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.configure_tileset_terrain(
            tileset_path=tileset_path,
            terrain_set=terrain_set,
            mode=mode,
            terrains=terrains,
            tile_peering_bits=tile_peering_bits,
            save_path=save_path,
        )

    async def diff_scene(
        self,
        scene_path: str | None = None,
        target_scene_path: str | None = None,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.diff_scene(
            scene_path=scene_path,
            target_scene_path=target_scene_path,
        )

    async def undo_action(
        self,
        history_id: int | None = None,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.undo_action(history_id=history_id)

    async def redo_action(
        self,
        history_id: int | None = None,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.redo_action(history_id=history_id)

    async def get_selected_nodes(
        self,
        include_properties: bool = True,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.get_selected_nodes(include_properties=include_properties)

    async def set_selected_nodes(
        self,
        node_paths: list[str],
        clear_previous: bool = True,
        inspect_primary: bool = True,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.set_selected_nodes(
            node_paths=node_paths,
            clear_previous=clear_previous,
            inspect_primary=inspect_primary,
        )

    async def audit_assets(
        self,
        include_extensions: list[str] | None = None,
        ignore_paths: list[str] | None = None,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.audit_assets(
            include_extensions=include_extensions,
            ignore_paths=ignore_paths,
        )

    async def clean_orphans(
        self,
        file_paths: list[str] | None = None,
        dry_run: bool = True,
        quarantine_folder: str | None = None,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.clean_orphans(
            file_paths=file_paths,
            dry_run=dry_run,
            quarantine_folder=quarantine_folder,
        )

    async def get_texture_info(
        self,
        texture_path: str,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.get_texture_info(texture_path=texture_path)

    async def run_gut_tests(
        self,
        test_dir: str = "res://test/unit",
        test_file: str | None = None,
        prefix: str = "test_",
        config_file: str | None = None,
        extra_args: list[str] | None = None,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.run_gut_tests(
            test_dir=test_dir,
            test_file=test_file,
            prefix=prefix,
            config_file=config_file,
            extra_args=extra_args,
        )

    async def generate_gut_test(
        self,
        target_script_path: str,
        test_file_path: str,
        test_methods: list[str] | None = None,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.generate_gut_test(
            target_script_path=target_script_path,
            test_file_path=test_file_path,
            test_methods=test_methods,
        )

    async def get_editor_layout(
        self,
        include_open_scenes: bool = True,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.get_editor_layout(include_open_scenes=include_open_scenes)

    async def set_editor_layout(
        self,
        main_screen: str | None = None,
        distraction_free_mode: bool | None = None,
        active_scene_path: str | None = None,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.set_editor_layout(
            main_screen=main_screen,
            distraction_free_mode=distraction_free_mode,
            active_scene_path=active_scene_path,
        )

    async def reparent_node(
        self,
        node_path: str,
        new_parent_path: str,
        keep_global_transform: bool = True,
        new_index: int | None = None,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.reparent_node(
            node_path=node_path,
            new_parent_path=new_parent_path,
            keep_global_transform=keep_global_transform,
            new_index=new_index,
        )

    async def duplicate_node(
        self,
        node_path: str,
        new_name: str | None = None,
        target_parent_path: str | None = None,
        duplicate_signals: bool = False,
        duplicate_groups: bool = True,
        duplicate_scripts: bool = True,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.duplicate_node(
            node_path=node_path,
            new_name=new_name,
            target_parent_path=target_parent_path,
            duplicate_signals=duplicate_signals,
            duplicate_groups=duplicate_groups,
            duplicate_scripts=duplicate_scripts,
        )

    async def set_node_owner(
        self,
        node_path: str,
        owner_node_path: str = ".",
        recursive: bool = True,
    ) -> StandardResult:
        client = await self.get_active_client()
        return await client.set_node_owner(
            node_path=node_path,
            owner_node_path=owner_node_path,
            recursive=recursive,
        )
