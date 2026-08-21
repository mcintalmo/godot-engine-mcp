"""Abstract base client for communicating with the Godot Engine."""

from abc import ABC, abstractmethod
from typing import Any

from godot_mcp.models.common import EngineMode, StandardResult


class GodotClient(ABC):
    """Abstract interface for Godot client implementations."""

    @property
    @abstractmethod
    def mode(self) -> EngineMode:
        """The communication mode of this client."""
        ...

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if this client backend is reachable and usable."""
        ...

    @abstractmethod
    async def get_version(self) -> StandardResult:
        """Retrieve engine version and project info."""
        ...

    @abstractmethod
    async def list_nodes(
        self,
        root_path: str = ".",
        max_depth: int = 4,
        include_properties: bool = False,
    ) -> StandardResult:
        """List nodes in the active scene tree."""
        ...

    @abstractmethod
    async def get_node(
        self,
        node_path: str,
        include_inherited_properties: bool = False,
    ) -> StandardResult:
        """Inspect a specific node's details and properties."""
        ...

    @abstractmethod
    async def create_node(
        self,
        type_name: str,
        name: str,
        parent_path: str = ".",
        properties: dict[str, Any] | None = None,
        script_path: str | None = None,
    ) -> StandardResult:
        """Create and add a new node to the active scene."""
        ...

    @abstractmethod
    async def modify_node(
        self,
        node_path: str,
        properties: dict[str, Any],
    ) -> StandardResult:
        """Modify properties of an existing node."""
        ...

    @abstractmethod
    async def delete_node(
        self,
        node_path: str,
    ) -> StandardResult:
        """Delete a node from the scene."""
        ...

    @abstractmethod
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
        """Connect or disconnect a signal between two nodes."""
        ...

    @abstractmethod
    async def instantiate_scene(
        self,
        scene_path: str,
        parent_path: str = ".",
        name: str | None = None,
        properties: dict[str, Any] | None = None,
    ) -> StandardResult:
        """Instantiate a .tscn scene file under a parent node."""
        ...

    @abstractmethod
    async def save_scene(
        self,
        scene_path: str | None = None,
    ) -> StandardResult:
        """Save the active scene or save as new path."""
        ...

    @abstractmethod
    async def open_scene(
        self,
        scene_path: str,
    ) -> StandardResult:
        """Open a scene in the Godot Editor."""
        ...

    @abstractmethod
    async def create_scene(
        self,
        scene_path: str,
        root_type: str = "Node2D",
        root_name: str = "Root",
        properties: dict[str, Any] | None = None,
        open_in_editor: bool = True,
    ) -> StandardResult:
        """Create a new scene file with its own dedicated root node."""
        ...

    @abstractmethod
    async def validate_script(
        self,
        script_path: str | None = None,
        code_content: str | None = None,
    ) -> StandardResult:
        """Validate GDScript syntax and check compilation errors."""
        ...

    @abstractmethod
    async def validate_shader(
        self,
        shader_path: str | None = None,
        shader_code: str | None = None,
    ) -> StandardResult:
        """Validate GDShader code syntax and compilation."""
        ...

    @abstractmethod
    async def get_class_info(
        self,
        class_name: str,
        include_inherited: bool = True,
        category: str = "all",
    ) -> StandardResult:
        """Query ClassDB for Godot engine class inheritance, properties, methods, and signals."""
        ...

    @abstractmethod
    async def get_documentation(
        self,
        query: str,
        category: str = "all",
    ) -> StandardResult:
        """Retrieve official Godot API documentation and signatures for classes, methods, and properties."""
        ...

    @abstractmethod
    async def create_script(
        self,
        path: str,
        content: str,
        inherits: str = "Node",
        attach_to_node: str | None = None,
    ) -> StandardResult:
        """Create or write a GDScript file."""
        ...

    @abstractmethod
    async def get_project_settings(
        self,
        section: str | None = None,
    ) -> StandardResult:
        """Read project.godot settings."""
        ...

    @abstractmethod
    async def set_project_setting(
        self,
        name: str,
        value: Any,
    ) -> StandardResult:
        """Set a project configuration setting."""
        ...

    @abstractmethod
    async def list_project_files(
        self,
        directory: str = "res://",
        extension_filter: list[str] | None = None,
        recursive: bool = True,
    ) -> StandardResult:
        """List files and resources in the project."""
        ...

    @abstractmethod
    async def run_project(
        self,
        scene_path: str | None = None,
        extra_arguments: list[str] | None = None,
        timeout_seconds: int = 10,
    ) -> StandardResult:
        """Run the project in debug mode and capture logs."""
        ...

    @abstractmethod
    async def run_tests(
        self,
        test_path: str | None = None,
        extra_arguments: list[str] | None = None,
        timeout_seconds: int = 30,
    ) -> StandardResult:
        """Run headless tests and parse results."""
        ...

    @abstractmethod
    async def take_screenshot(
        self,
        viewport_type: str = "main_2d_3d",
        output_path: str | None = None,
    ) -> StandardResult:
        """Capture a screenshot of the active viewport or editor."""
        ...

    @abstractmethod
    async def create_material(
        self,
        material_path: str,
        material_type: str = "StandardMaterial3D",
        properties: dict[str, Any] | None = None,
        shader_path: str | None = None,
        shader_code: str | None = None,
        assign_to_node_path: str | None = None,
    ) -> StandardResult:
        """Create and configure a Godot Material resource (.tres) and optionally attach to node."""
        ...

    @abstractmethod
    async def reimport_asset(
        self,
        asset_path: str,
        preset: str | None = None,
        custom_params: dict[str, Any] | None = None,
    ) -> StandardResult:
        """Reimport an asset in Godot and optionally apply import preset parameters."""
        ...

    @abstractmethod
    async def create_collision_polygon(
        self,
        points: list[list[float]],
        polygon_type: str = "2D",
        parent_node_path: str = ".",
        node_name: str = "CollisionPolygon",
        depth: float = 1.0,
        disabled: bool = False,
    ) -> StandardResult:
        """Generate a 2D or 3D collision polygon from vertex coordinates and attach to scene node."""
        ...

    @abstractmethod
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
        """Create and configure an Animation resource with tracks and keyframes."""
        ...

    @abstractmethod
    async def set_tilemap_cells(
        self,
        node_path: str,
        cells: list[dict[str, Any]],
        clear_before_paint: bool = False,
    ) -> StandardResult:
        """Batch-paint or erase tile cells on a TileMapLayer or TileMap node."""
        ...

    @abstractmethod
    async def get_tilemap_cells(
        self,
        node_path: str,
        region: list[int] | None = None,
    ) -> StandardResult:
        """Query painted tile cells and bounding geometry from a TileMapLayer or TileMap."""
        ...

    @abstractmethod
    async def create_tilemap_layer(
        self,
        name: str = "TileMapLayer",
        parent_node_path: str = ".",
        tile_set_path: str | None = None,
    ) -> StandardResult:
        """Create a new TileMapLayer node and attach optional TileSet resource."""
        ...

    @abstractmethod
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
        """Bake a 2D or 3D navigation mesh on a NavigationRegion node."""
        ...

    @abstractmethod
    async def create_navigation_region(
        self,
        name: str = "NavigationRegion3D",
        dimension: str = "3D",
        parent_node_path: str = ".",
        navmesh_path: str | None = None,
    ) -> StandardResult:
        """Create a new NavigationRegion3D or NavigationRegion2D node."""
        ...

    @abstractmethod
    async def query_lsp(
        self,
        file_path: str,
        query_type: str = "symbols",
        line: int = 1,
        character: int = 1,
        symbol_name: str | None = None,
    ) -> StandardResult:
        """Query symbols, definitions, references, or hover documentation via Godot LSP."""
        ...

    @abstractmethod
    async def rename_lsp_symbol(
        self,
        file_path: str,
        line: int,
        character: int,
        new_name: str,
    ) -> StandardResult:
        """Perform a cross-file semantic rename of a GDScript symbol via Godot LSP."""
        ...

    @abstractmethod
    async def get_performance_metrics(
        self,
        category: str = "all",
        include_custom_monitors: bool = True,
    ) -> StandardResult:
        """Query real-time Godot engine performance metrics and telemetry."""
        ...

    @abstractmethod
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
        """Create and configure a Godot 4 Theme resource (.tres) with custom styles."""
        ...

    @abstractmethod
    async def apply_theme_override(
        self,
        node_path: str,
        override_type: str,
        item_name: str,
        value: Any,
    ) -> StandardResult:
        """Apply a theme override (stylebox, color, constant, font_size) directly to a Control node."""
        ...

    @abstractmethod
    async def get_audio_layout(
        self,
        include_effects: bool = True,
    ) -> StandardResult:
        """Query all buses, volume levels, routing, and effects in AudioServer."""
        ...

    @abstractmethod
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
        """Create or configure an audio bus in AudioServer."""
        ...

    @abstractmethod
    async def set_bus_effect(
        self,
        bus_name: str,
        effect_type: str,
        effect_index: int | None = None,
        enabled: bool = True,
        properties: dict[str, Any] | None = None,
        save_layout_path: str | None = None,
    ) -> StandardResult:
        """Add or modify an AudioEffect on an AudioServer bus."""
        ...

    @abstractmethod
    async def play_scene(
        self,
        mode: str = "main",
        custom_scene_path: str | None = None,
    ) -> StandardResult:
        """Launch interactive scene playback."""
        ...

    @abstractmethod
    async def stop_scene(self) -> StandardResult:
        """Stop running scene playback."""
        ...

    @abstractmethod
    async def get_play_state(self) -> StandardResult:
        """Query current playback state, time scale, and pause status."""
        ...

    @abstractmethod
    async def set_play_state(
        self,
        pause: bool | None = None,
        time_scale: float | None = None,
        step_frames: int | None = None,
    ) -> StandardResult:
        """Set pause state, simulation speed, or step frames."""
        ...

    @abstractmethod
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
        """Execute a 3D raycast in the active physics world."""
        ...

    @abstractmethod
    async def cast_shape_3d(
        self,
        shape_type: str,
        shape_params: dict[str, float],
        origin: tuple[float, float, float],
        motion: tuple[float, float, float] | None = None,
        collision_mask: int = 0xFFFFFFFF,
        max_results: int = 32,
    ) -> StandardResult:
        """Execute a 3D shape sweep or overlap query."""
        ...

    @abstractmethod
    async def get_body_physics_state_3d(
        self,
        node_path: str,
    ) -> StandardResult:
        """Retrieve live physics body telemetry (velocity, mass, contacts, sleeping)."""
        ...

    @abstractmethod
    async def set_physics_debug_mode(
        self,
        visible_collision_shapes: bool | None = None,
        visible_paths: bool | None = None,
        visible_navigation: bool | None = None,
        collision_debug_color: str | None = None,
    ) -> StandardResult:
        """Toggle physics debug rendering and wireframe collision shapes."""
        ...

    @abstractmethod
    async def get_input_actions(
        self,
        filter_prefix: str | None = None,
    ) -> StandardResult:
        """Query project input actions and event bindings."""
        ...

    @abstractmethod
    async def configure_input_action(
        self,
        action_name: str,
        deadzone: float = 0.5,
        events: list[dict[str, Any]] | None = None,
        replace_existing: bool = True,
        save_to_project_settings: bool = True,
    ) -> StandardResult:
        """Create or configure an input action with key/button/axis bindings."""
        ...

    @abstractmethod
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
        """Configure post-processing, lighting, and skybox in Environment resource or WorldEnvironment node."""
        ...

    @abstractmethod
    async def set_editor_selection(
        self,
        node_paths: list[str],
        clear_previous: bool = True,
    ) -> StandardResult:
        """Select nodes in the Godot Scene dock."""
        ...

    @abstractmethod
    async def focus_node(
        self,
        node_path: str,
        main_screen: str | None = None,
    ) -> StandardResult:
        """Focus a node in Inspector and 2D/3D editor screen."""
        ...

    @abstractmethod
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
        """Instantiate a 3D model asset (.glb, .gltf, .blend) into the scene tree."""
        ...

    @abstractmethod
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
        """Configure .import settings for a 3D model file and trigger reimport."""
        ...

    @abstractmethod
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
        """Create or configure a VFX particle system or ParticleProcessMaterial resource."""
        ...

    @abstractmethod
    async def get_export_presets(self) -> StandardResult:
        """Query configured export presets from export_presets.cfg."""
        ...

    @abstractmethod
    async def export_project(
        self,
        preset_name: str,
        output_path: str,
        debug: bool = False,
    ) -> StandardResult:
        """Export project binary headlessly for specified preset target."""
        ...

    @abstractmethod
    async def get_autoloads(self) -> StandardResult:
        """Query all autoload singletons from project.godot."""
        ...

    @abstractmethod
    async def set_autoload(
        self,
        name: str,
        path: str | None = None,
        is_singleton: bool = True,
        remove: bool = False,
    ) -> StandardResult:
        """Add, update, or remove an autoload singleton in project.godot."""
        ...

    @abstractmethod
    async def get_node_signals(
        self,
        node_path: str,
        include_inherited: bool = True,
    ) -> StandardResult:
        """Introspect signal definitions on a target node."""
        ...

    @abstractmethod
    async def get_signal_connections(
        self,
        node_path: str,
        signal_name: str | None = None,
        incoming: bool = True,
        outgoing: bool = True,
    ) -> StandardResult:
        """Query incoming and outgoing signal connections for a node."""
        ...

    @abstractmethod
    async def evaluate_expression(
        self,
        expression: str,
        node_path: str | None = None,
        input_variables: dict[str, Any] | None = None,
    ) -> StandardResult:
        """Safely evaluate a runtime GDScript expression."""
        ...

    @abstractmethod
    async def create_shader(
        self,
        path: str,
        shader_type: str = "spatial",
        code: str | None = None,
        create_material: bool = True,
        material_save_path: str | None = None,
    ) -> StandardResult:
        """Create a .gdshader file and optional ShaderMaterial."""
        ...

    @abstractmethod
    async def set_shader_param(
        self,
        parameter_name: str,
        value: Any,
        node_path: str | None = None,
        material_path: str | None = None,
    ) -> StandardResult:
        """Inspect and update a uniform parameter on a ShaderMaterial."""
        ...

    @abstractmethod
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
        """Create or configure an AnimationTree and State Machine."""
        ...

    @abstractmethod
    async def get_translations(
        self,
        locale_filter: str | None = None,
    ) -> StandardResult:
        """Query configured translation tables in ProjectSettings."""
        ...

    @abstractmethod
    async def add_translation(
        self,
        translation_path: str,
        test_locale: str | None = None,
    ) -> StandardResult:
        """Register a translation table in ProjectSettings."""
        ...

    @abstractmethod
    async def get_uid(
        self,
        path: str,
    ) -> StandardResult:
        """Convert a resource path into its native Godot uid:// identifier."""
        ...

    @abstractmethod
    async def resolve_uid(
        self,
        uid: str,
    ) -> StandardResult:
        """Resolve a uid:// identifier back into its file path."""
        ...

    @abstractmethod
    async def get_dependencies(
        self,
        path: str,
    ) -> StandardResult:
        """Query the complete dependency list for a scene, resource, or script."""
        ...

    @abstractmethod
    async def get_plugins(
        self,
        enabled_only: bool = False,
    ) -> StandardResult:
        """Discover installed editor plugins in res://addons/."""
        ...

    @abstractmethod
    async def set_plugin_status(
        self,
        plugin_name: str,
        enabled: bool = True,
    ) -> StandardResult:
        """Enable or disable an editor plugin."""
        ...

    @abstractmethod
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
        """Create or configure a NavigationObstacle2D/3D node."""
        ...

    @abstractmethod
    async def configure_tileset_terrain(
        self,
        tileset_path: str,
        terrain_set: int = 0,
        mode: str = "match_corners_and_sides",
        terrains: list[dict[str, Any]] | None = None,
        tile_peering_bits: list[dict[str, Any]] | None = None,
        save_path: str | None = None,
    ) -> StandardResult:
        """Configure TileSet terrain sets, terrain modes, and autotiling peering bits."""
        ...

    @abstractmethod
    async def diff_scene(
        self,
        scene_path: str | None = None,
        target_scene_path: str | None = None,
    ) -> StandardResult:
        """Diff active scene against disk or compare two .tscn scene files."""
        ...

    @abstractmethod
    async def undo_action(
        self,
        history_id: int | None = None,
    ) -> StandardResult:
        """Revert the last action in the active scene or global undo history."""
        ...

    @abstractmethod
    async def redo_action(
        self,
        history_id: int | None = None,
    ) -> StandardResult:
        """Redo the previously undone action in history."""
        ...

    @abstractmethod
    async def get_selected_nodes(
        self,
        include_properties: bool = True,
    ) -> StandardResult:
        """Query currently selected nodes in the editor SceneTree."""
        ...

    @abstractmethod
    async def set_selected_nodes(
        self,
        node_paths: list[str],
        clear_previous: bool = True,
        inspect_primary: bool = True,
    ) -> StandardResult:
        """Set active node selection in the editor SceneTree."""
        ...

    @abstractmethod
    async def audit_assets(
        self,
        include_extensions: list[str] | None = None,
        ignore_paths: list[str] | None = None,
    ) -> StandardResult:
        """Scan project assets for orphans, broken dependencies, and statistics."""
        ...

    @abstractmethod
    async def clean_orphans(
        self,
        file_paths: list[str] | None = None,
        dry_run: bool = True,
        quarantine_folder: str | None = None,
    ) -> StandardResult:
        """Clean or quarantine unreferenced orphan files."""
        ...

    @abstractmethod
    async def get_texture_info(
        self,
        texture_path: str,
    ) -> StandardResult:
        """Inspect dimensions, format, mipmaps, and estimated VRAM for a texture."""
        ...
