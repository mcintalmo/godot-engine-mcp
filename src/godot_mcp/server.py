"""FastMCP Server setup and tool registrations for Godot Engine."""

import json

from mcp.server import MCPServer
from mcp.types import ToolAnnotations

from godot_mcp.client.base import GodotClient
from godot_mcp.client.manager import ClientManager
from godot_mcp.config import GodotConfig
from godot_mcp.models.anim_tree import ConfigureAnimationTreeInput
from godot_mcp.models.animation import CreateAnimationInput
from godot_mcp.models.asset import (
    CreateCollisionPolygonInput,
    ReimportAssetInput,
)
from godot_mcp.models.asset_audit import (
    AuditAssetsInput,
    CleanOrphansInput,
    GetTextureInfoInput,
)
from godot_mcp.models.audio import (
    ConfigureAudioBusInput,
    GetAudioLayoutInput,
    SetBusEffectInput,
)
from godot_mcp.models.autoload import (
    GetAutoloadsInput,
    SetAutoloadInput,
)
from godot_mcp.models.camera_rendering import (
    CaptureViewportInput,
    ConfigureCameraInput,
    ConfigureRenderSettingsInput,
)
from godot_mcp.models.dcc_asset import (
    ConfigureGLTFImportInput,
    InstantiateModelInput,
)
from godot_mcp.models.debug import (
    RunProjectInput,
    RunTestsInput,
    TakeScreenshotInput,
)
from godot_mcp.models.e2e_automation import (
    AssertNodeStateInput,
    FindElementsInput,
    InteractNodeInput,
    WaitForConditionInput,
)
from godot_mcp.models.editor_focus import (
    FocusNodeInput,
    SetEditorSelectionInput,
)
from godot_mcp.models.editor_history import (
    RedoInput,
    UndoInput,
)
from godot_mcp.models.editor_layout import (
    GetEditorLayoutInput,
    SetEditorLayoutInput,
)
from godot_mcp.models.editor_selection import (
    GetSelectedNodesInput,
    SetSelectedNodesInput,
)
from godot_mcp.models.environment import ConfigureEnvironmentInput
from godot_mcp.models.export_build import (
    ExportProjectInput,
    GetExportPresetsInput,
)
from godot_mcp.models.gridmap_path import (
    ConfigureGridMapInput,
    CreateCurvePathInput,
)
from godot_mcp.models.gut_test import (
    GenerateGUTTestInput,
    RunGUTTestsInput,
)
from godot_mcp.models.input_map import (
    ConfigureInputActionInput,
    GetInputActionsInput,
)
from godot_mcp.models.input_simulation import (
    ClearDebugShapesInput,
    DrawDebugShapesInput,
    SimulateInputInput,
)
from godot_mcp.models.localization import (
    AddTranslationInput,
    GetTranslationsInput,
)
from godot_mcp.models.lsp import (
    LSPQueryInput,
    LSPRenameInput,
)
from godot_mcp.models.material import CreateMaterialInput
from godot_mcp.models.multiplayer import (
    ConfigureMultiplayerSpawnerInput,
    ConfigureMultiplayerSynchronizerInput,
    SimulateNetworkConditionsInput,
)
from godot_mcp.models.nav_obstacle import ConfigureNavigationObstacleInput
from godot_mcp.models.navigation import (
    BakeNavMeshInput,
    CreateNavigationRegionInput,
)
from godot_mcp.models.particles import ConfigureParticlesInput
from godot_mcp.models.performance import GetPerformanceMetricsInput
from godot_mcp.models.physics import (
    CastRay3DInput,
    CastShape3DInput,
    GetBodyPhysicsState3DInput,
    SetPhysicsDebugModeInput,
)
from godot_mcp.models.play import (
    GetPlayStateInput,
    PlaySceneInput,
    SetPlayStateInput,
    StopSceneInput,
)
from godot_mcp.models.plugin_mgr import (
    GetPluginsInput,
    SetPluginStatusInput,
)
from godot_mcp.models.profiling_diagnostics import (
    AuditOrphanNodesInput,
    CaptureProfilerTraceInput,
    InspectVRAMUsageInput,
)
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
from godot_mcp.models.runtime_eval import EvaluateExpressionInput
from godot_mcp.models.scene import (
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
from godot_mcp.models.scene_diff import DiffSceneInput
from godot_mcp.models.scene_hierarchy import (
    DuplicateNodeInput,
    ReparentNodeInput,
    SetNodeOwnerInput,
)
from godot_mcp.models.script import (
    CreateScriptInput,
    ValidateScriptInput,
)
from godot_mcp.models.script_lifecycle import (
    AttachScriptInput,
    GetNodeScriptInfoInput,
    ReloadScriptsInput,
)
from godot_mcp.models.shader import (
    CreateShaderInput,
    SetShaderParamInput,
)
from godot_mcp.models.signal_wire import (
    ConnectSignalInput,
    GetNodeSignalsInput,
    GetSignalConnectionsInput,
)
from godot_mcp.models.theme import (
    ApplyThemeOverrideInput,
    CreateThemeInput,
)
from godot_mcp.models.tilemap import (
    CreateTileMapLayerInput,
    GetTileMapCellsInput,
    SetTileMapCellsInput,
)
from godot_mcp.models.tileset_terrain import ConfigureTileSetTerrainInput
from godot_mcp.models.uid_dep import (
    GetDependenciesInput,
    GetUIDInput,
    ResolveUIDInput,
)
from godot_mcp.tools.anim_tree_tools import handle_configure_animation_tree
from godot_mcp.tools.animation_tools import handle_create_animation
from godot_mcp.tools.asset_audit_tools import (
    handle_audit_assets,
    handle_clean_orphans,
    handle_get_texture_info,
)
from godot_mcp.tools.asset_tools import (
    handle_create_collision_polygon,
    handle_reimport_asset,
)
from godot_mcp.tools.audio_tools import (
    handle_configure_audio_bus,
    handle_get_audio_layout,
    handle_set_bus_effect,
)
from godot_mcp.tools.autoload_tools import (
    handle_get_autoloads,
    handle_set_autoload,
)
from godot_mcp.tools.build_tools import (
    handle_export_project,
    handle_get_export_presets,
)
from godot_mcp.tools.camera_rendering_tools import (
    handle_capture_viewport,
    handle_configure_camera,
    handle_configure_render_settings,
)
from godot_mcp.tools.dcc_tools import (
    handle_configure_gltf_import,
    handle_instantiate_model,
)
from godot_mcp.tools.debug_tools import (
    handle_run_project,
    handle_run_tests,
    handle_take_screenshot,
)
from godot_mcp.tools.e2e_automation_tools import (
    handle_assert_node_state,
    handle_find_elements,
    handle_interact_node,
    handle_wait_for_condition,
)
from godot_mcp.tools.editor_history_tools import (
    handle_redo,
    handle_undo,
)
from godot_mcp.tools.editor_layout_tools import (
    handle_get_editor_layout,
    handle_set_editor_layout,
)
from godot_mcp.tools.editor_selection_tools import (
    handle_get_selected_nodes,
    handle_set_selected_nodes,
)
from godot_mcp.tools.editor_tools import (
    handle_focus_node,
    handle_set_editor_selection,
)
from godot_mcp.tools.environment_tools import handle_configure_environment
from godot_mcp.tools.eval_tools import handle_evaluate_expression
from godot_mcp.tools.gridmap_path_tools import (
    handle_configure_gridmap,
    handle_create_curve_path,
)
from godot_mcp.tools.gut_test_tools import (
    handle_generate_gut_test,
    handle_run_gut_tests,
)
from godot_mcp.tools.input_simulation_tools import (
    handle_clear_debug_shapes,
    handle_draw_debug_shapes,
    handle_simulate_input,
)
from godot_mcp.tools.input_tools import (
    handle_configure_input_action,
    handle_get_input_actions,
)
from godot_mcp.tools.localization_tools import (
    handle_add_translation,
    handle_get_translations,
)
from godot_mcp.tools.lsp_tools import (
    handle_lsp_query,
    handle_lsp_rename,
)
from godot_mcp.tools.material_tools import handle_create_material
from godot_mcp.tools.multiplayer_tools import (
    handle_configure_multiplayer_spawner,
    handle_configure_multiplayer_synchronizer,
    handle_simulate_network_conditions,
)
from godot_mcp.tools.nav_obstacle_tools import (
    handle_configure_navigation_obstacle,
)
from godot_mcp.tools.navigation_tools import (
    handle_bake_navmesh,
    handle_create_navigation_region,
)
from godot_mcp.tools.particle_tools import handle_configure_particles
from godot_mcp.tools.performance_tools import handle_get_performance_metrics
from godot_mcp.tools.physics_tools import (
    handle_cast_ray_3d,
    handle_cast_shape_3d,
    handle_get_body_physics_state_3d,
    handle_set_physics_debug_mode,
)
from godot_mcp.tools.play_tools import (
    handle_get_play_state,
    handle_play_scene,
    handle_set_play_state,
    handle_stop_scene,
)
from godot_mcp.tools.plugin_tools import (
    handle_get_plugins,
    handle_set_plugin_status,
)
from godot_mcp.tools.profiling_diagnostics_tools import (
    handle_audit_orphan_nodes,
    handle_capture_profiler_trace,
    handle_inspect_vram_usage,
)
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
from godot_mcp.tools.scene_diff_tools import handle_diff_scene
from godot_mcp.tools.scene_hierarchy_tools import (
    handle_duplicate_node,
    handle_reparent_node,
    handle_set_node_owner,
)
from godot_mcp.tools.scene_tools import (
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
from godot_mcp.tools.script_lifecycle_tools import (
    handle_attach_script,
    handle_get_node_script_info,
    handle_reload_scripts,
)
from godot_mcp.tools.script_tools import (
    handle_create_script,
    handle_validate_script,
)
from godot_mcp.tools.shader_tools import (
    handle_create_shader,
    handle_set_shader_param,
)
from godot_mcp.tools.signal_tools import (
    handle_connect_signal,
    handle_get_node_signals,
    handle_get_signal_connections,
)
from godot_mcp.tools.theme_tools import (
    handle_apply_theme_override,
    handle_create_theme,
)
from godot_mcp.tools.tilemap_tools import (
    handle_create_tilemap_layer,
    handle_get_tilemap_cells,
    handle_set_tilemap_cells,
)
from godot_mcp.tools.tileset_terrain_tools import handle_configure_tileset_terrain
from godot_mcp.tools.uid_tools import (
    handle_get_dependencies,
    handle_get_uid,
    handle_resolve_uid,
)


def create_server(
    client: GodotClient | None = None, config: GodotConfig | None = None
) -> MCPServer:
    """Create and configure the MCPServer with all Godot tools registered."""
    active_client = client or ClientManager(config or GodotConfig.load())

    server = MCPServer(
        name="godot_mcp",
        instructions="Model Context Protocol (MCP) server for inspecting and controlling the Godot Engine 4.7+.",
    )

    # --- Project & Version Tools ---

    @server.tool(
        name="godot_get_version",
        annotations=ToolAnnotations(
            title="Get Godot Engine Version",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def get_version(params: GetVersionInput) -> str:
        """Get the current Godot Engine version, build info, connection mode, and project path."""
        return await handle_get_version(active_client, params)

    @server.tool(
        name="godot_get_project_settings",
        annotations=ToolAnnotations(
            title="Get Project Settings",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def get_project_settings(params: GetProjectSettingsInput) -> str:
        """Query settings from project.godot (e.g. application name, display window, physics, autoloads)."""
        return await handle_get_project_settings(active_client, params)

    @server.tool(
        name="godot_set_project_setting",
        annotations=ToolAnnotations(
            title="Set Project Setting",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def set_project_setting(params: SetProjectSettingInput) -> str:
        """Write or update a configuration setting in project.godot."""
        return await handle_set_project_setting(active_client, params)

    @server.tool(
        name="godot_list_project_files",
        annotations=ToolAnnotations(
            title="List Project Files",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def list_project_files(params: ListProjectFilesInput) -> str:
        """List and search files, scenes (.tscn), scripts (.gd), and assets in the Godot project."""
        return await handle_list_project_files(active_client, params)

    # --- Scene & Node Manipulation Tools ---

    @server.tool(
        name="godot_list_nodes",
        annotations=ToolAnnotations(
            title="List Scene Nodes",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def list_nodes(params: ListNodesInput) -> str:
        """List the node hierarchy of the active scene in the Godot editor."""
        return await handle_list_nodes(active_client, params)

    @server.tool(
        name="godot_get_node",
        annotations=ToolAnnotations(
            title="Get Node Details",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def get_node(params: GetNodeInput) -> str:
        """Retrieve detailed information about a specific node (type, properties, attached script, signals)."""
        return await handle_get_node(active_client, params)

    @server.tool(
        name="godot_create_node",
        annotations=ToolAnnotations(
            title="Create Node in Scene",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def create_node(params: CreateNodeInput) -> str:
        """Add a new node of any Godot class (e.g. Sprite2D, CharacterBody2D, Camera3D, Control) to the active scene."""
        return await handle_create_node(active_client, params)

    @server.tool(
        name="godot_modify_node",
        annotations=ToolAnnotations(
            title="Modify Node Properties",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def modify_node(params: ModifyNodeInput) -> str:
        """Update properties (transform, visibility, exports) of an existing node in the active scene."""
        return await handle_modify_node(active_client, params)

    @server.tool(
        name="godot_delete_node",
        annotations=ToolAnnotations(
            title="Delete Node from Scene",
            read_only_hint=False,
            destructive_hint=True,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def delete_node(params: DeleteNodeInput) -> str:
        """Safely remove a node from the active scene with Undo/Redo support."""
        return await handle_delete_node(active_client, params)

    @server.tool(
        name="godot_connect_signal",
        annotations=ToolAnnotations(
            title="Connect Node Signal",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def connect_signal(params: ConnectSignalInput) -> str:
        """Connect a signal from a source node to a target node method."""
        return await handle_connect_signal(active_client, params)

    @server.tool(
        name="godot_instantiate_scene",
        annotations=ToolAnnotations(
            title="Instantiate Packed Scene",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def instantiate_scene(params: InstantiateSceneInput) -> str:
        """Instantiate a .tscn packed scene resource into the active scene tree."""
        return await handle_instantiate_scene(active_client, params)

    @server.tool(
        name="godot_save_scene",
        annotations=ToolAnnotations(
            title="Save Scene",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def save_scene(params: SaveSceneInput) -> str:
        """Save the active scene or save to a specified .tscn file."""
        return await handle_save_scene(active_client, params)

    @server.tool(
        name="godot_open_scene",
        annotations=ToolAnnotations(
            title="Open Scene in Editor",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def open_scene(params: OpenSceneInput) -> str:
        """Open a .tscn scene file in the active Godot Editor session."""
        return await handle_open_scene(active_client, params)

    @server.tool(
        name="godot_create_scene",
        annotations=ToolAnnotations(
            title="Create New Scene",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def create_scene(params: CreateSceneInput) -> str:
        """Create a brand new scene file with its own dedicated root node and open it in editor."""
        return await handle_create_scene(active_client, params)

    # --- Script Tools ---

    @server.tool(
        name="godot_validate_script",
        annotations=ToolAnnotations(
            title="Validate GDScript",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def validate_script(params: ValidateScriptInput) -> str:
        """Check GDScript code or file for syntax errors, type errors, and compilation diagnostics."""
        return await handle_validate_script(active_client, params)

    @server.tool(
        name="godot_create_script",
        annotations=ToolAnnotations(
            title="Create GDScript",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def create_script(params: CreateScriptInput) -> str:
        """Create or update a GDScript file and optionally attach it to a node in the active scene."""
        return await handle_create_script(active_client, params)

    @server.tool(
        name="godot_validate_shader",
        annotations=ToolAnnotations(
            title="Validate GDShader",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def validate_shader(params: ValidateShaderInput) -> str:
        """Check .gdshader code or file for syntax errors and compilation diagnostics."""
        return await handle_validate_shader(active_client, params)

    # --- Reflection & Documentation Tools ---

    @server.tool(
        name="godot_get_class_info",
        annotations=ToolAnnotations(
            title="Get ClassDB Metadata",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def get_class_info(params: GetClassInfoInput) -> str:
        """Query Godot ClassDB for class inheritance, properties, methods, signals, enums, and constants."""
        return await handle_get_class_info(active_client, params)

    @server.tool(
        name="godot_get_documentation",
        annotations=ToolAnnotations(
            title="Get Engine Documentation",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def get_documentation(params: GetDocumentationInput) -> str:
        """Retrieve official Godot API documentation, method signatures, and property specifications."""
        return await handle_get_documentation(active_client, params)

    # --- Debugging & Execution Tools ---

    @server.tool(
        name="godot_run_project",
        annotations=ToolAnnotations(
            title="Run Project in Debug Mode",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=True,
        ),
    )
    async def run_project(params: RunProjectInput) -> str:
        """Launch the Godot project in debug mode, streaming execution logs and error output."""
        return await handle_run_project(active_client, params)

    @server.tool(
        name="godot_run_tests",
        annotations=ToolAnnotations(
            title="Run Headless Tests",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=True,
        ),
    )
    async def run_tests(params: RunTestsInput) -> str:
        """Execute headless test suites or GDScript test runners and parse test results."""
        return await handle_run_tests(active_client, params)

    @server.tool(
        name="godot_take_screenshot",
        annotations=ToolAnnotations(
            title="Take Viewport Screenshot",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def take_screenshot(params: TakeScreenshotInput) -> str:
        """Capture a screenshot of the active Godot 2D/3D viewport or running game for visual inspection."""
        return await handle_take_screenshot(active_client, params)

    # --- Material & Shader Tools ---

    @server.tool(
        name="godot_create_material",
        annotations=ToolAnnotations(
            title="Create and Configure Material",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def create_material(params: CreateMaterialInput) -> str:
        """Create and configure a Godot Material resource (.tres) (StandardMaterial3D, ShaderMaterial, CanvasItemMaterial, ORMMaterial3D) with PBR properties and optional scene node attachment."""
        return await handle_create_material(active_client, params)

    @server.tool(
        name="godot_reimport_asset",
        annotations=ToolAnnotations(
            title="Reimport Asset with Configuration Presets",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def reimport_asset(params: ReimportAssetInput) -> str:
        """Reimport an asset in Godot with optional import presets (e.g. pixel_art_2d, high_quality_3d, uncompressed_audio) or custom .import parameter overrides."""
        return await handle_reimport_asset(active_client, params)

    @server.tool(
        name="godot_create_collision_polygon",
        annotations=ToolAnnotations(
            title="Generate Collision Polygon",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def create_collision_polygon(
        params: CreateCollisionPolygonInput,
    ) -> str:
        """Generate a 2D or 3D collision polygon (CollisionPolygon2D or CollisionPolygon3D) from vertex coordinates and attach to the target parent node in the active scene."""
        return await handle_create_collision_polygon(active_client, params)

    @server.tool(
        name="godot_create_animation",
        annotations=ToolAnnotations(
            title="Create Animation Tracks and Keyframes",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def create_animation(params: CreateAnimationInput) -> str:
        """Create and configure a Godot Animation resource with property tracks, 3D transform tracks, or method call tracks, with keyframes, easing curves, and optional AnimationPlayer attachment or .tres disk saving."""
        return await handle_create_animation(active_client, params)

    @server.tool(
        name="godot_create_tilemap_layer",
        annotations=ToolAnnotations(
            title="Create TileMapLayer Node",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def create_tilemap_layer(params: CreateTileMapLayerInput) -> str:
        """Create a TileMapLayer node in the active scene and optionally attach an existing TileSet resource (.tres)."""
        return await handle_create_tilemap_layer(active_client, params)

    @server.tool(
        name="godot_set_tilemap_cells",
        annotations=ToolAnnotations(
            title="Batch-Paint TileMapLayer Cells",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def set_tilemap_cells(params: SetTileMapCellsInput) -> str:
        """Batch-paint or erase tile cells on a TileMapLayer or TileMap node with grid coordinates, source IDs, atlas coordinates, and alternative tile IDs."""
        return await handle_set_tilemap_cells(active_client, params)

    @server.tool(
        name="godot_get_tilemap_cells",
        annotations=ToolAnnotations(
            title="Query TileMapLayer Cells",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def get_tilemap_cells(params: GetTileMapCellsInput) -> str:
        """Query used tile cells, source IDs, atlas coordinates, and bounding rectangles from a TileMapLayer or TileMap node."""
        return await handle_get_tilemap_cells(active_client, params)

    @server.tool(
        name="godot_create_navigation_region",
        annotations=ToolAnnotations(
            title="Create Navigation Region",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def create_navigation_region(
        params: CreateNavigationRegionInput,
    ) -> str:
        """Create a NavigationRegion3D or NavigationRegion2D node in the active scene and attach a NavigationMesh / NavigationPolygon resource."""
        return await handle_create_navigation_region(active_client, params)

    @server.tool(
        name="godot_bake_navmesh",
        annotations=ToolAnnotations(
            title="Bake Navigation Mesh",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def bake_navmesh(params: BakeNavMeshInput) -> str:
        """Configure agent parameters (radius, height, climb, slope, cell size) and bake a 2D or 3D navigation mesh on a target NavigationRegion node."""
        return await handle_bake_navmesh(active_client, params)

    @server.tool(
        name="godot_lsp_query",
        annotations=ToolAnnotations(
            title="Godot LSP Semantic Query",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def lsp_query(params: LSPQueryInput) -> str:
        """Query GDScript semantic symbols, go-to-definition, find all references, or inspect hover docstrings and type signatures via Godot LSP."""
        return await handle_lsp_query(active_client, params)

    @server.tool(
        name="godot_lsp_rename",
        annotations=ToolAnnotations(
            title="Godot LSP Semantic Rename",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def lsp_rename(params: LSPRenameInput) -> str:
        """Perform a cross-file semantic rename of a GDScript symbol across all referencing project files."""
        return await handle_lsp_rename(active_client, params)

    @server.tool(
        name="godot_get_performance_metrics",
        annotations=ToolAnnotations(
            title="Get Performance Metrics",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def get_performance_metrics(params: GetPerformanceMetricsInput) -> str:
        """Query real-time Godot engine performance metrics (FPS, process/physics frame times, draw calls, VRAM, static memory, and orphan node leak tracking)."""
        return await handle_get_performance_metrics(active_client, params)

    @server.tool(
        name="godot_create_theme",
        annotations=ToolAnnotations(
            title="Create Theme Resource",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def create_theme(params: CreateThemeInput) -> str:
        """Create and configure a Godot 4 Theme resource (.tres) with custom StyleBoxFlat definitions, colors, constants, and fonts."""
        return await handle_create_theme(active_client, params)

    @server.tool(
        name="godot_apply_theme_override",
        annotations=ToolAnnotations(
            title="Apply Theme Override to Node",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def apply_theme_override(params: ApplyThemeOverrideInput) -> str:
        """Apply a styling override (StyleBoxFlat, color, constant, font_size) directly to a target Control node in the active scene."""
        return await handle_apply_theme_override(active_client, params)

    @server.tool(
        name="godot_get_audio_layout",
        annotations=ToolAnnotations(
            title="Get Audio Bus Layout",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def get_audio_layout(params: GetAudioLayoutInput) -> str:
        """Query all AudioServer buses, volume levels, routing send destinations, and active effect chains."""
        return await handle_get_audio_layout(active_client, params)

    @server.tool(
        name="godot_configure_audio_bus",
        annotations=ToolAnnotations(
            title="Configure Audio Bus",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def configure_audio_bus(params: ConfigureAudioBusInput) -> str:
        """Create or configure an audio bus in AudioServer (volume, routing send, mute, solo, effect bypass, .tres layout export)."""
        return await handle_configure_audio_bus(active_client, params)

    @server.tool(
        name="godot_set_bus_effect",
        annotations=ToolAnnotations(
            title="Set Audio Bus Effect",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def set_bus_effect(params: SetBusEffectInput) -> str:
        """Add or configure an AudioEffect (Reverb, Chorus, Delay, LowPassFilter, EQ, Compressor, Limiter) on an audio bus."""
        return await handle_set_bus_effect(active_client, params)

    @server.tool(
        name="godot_play_scene",
        annotations=ToolAnnotations(
            title="Play Scene",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def play_scene(params: PlaySceneInput) -> str:
        """Launch interactive game playback (main scene, active tab scene, or custom .tscn)."""
        return await handle_play_scene(active_client, params)

    @server.tool(
        name="godot_stop_scene",
        annotations=ToolAnnotations(
            title="Stop Scene Playback",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def stop_scene(params: StopSceneInput) -> str:
        """Stop currently running interactive scene playback."""
        return await handle_stop_scene(active_client, params)

    @server.tool(
        name="godot_get_play_state",
        annotations=ToolAnnotations(
            title="Get Play State",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def get_play_state(params: GetPlayStateInput) -> str:
        """Query current interactive playback status, simulation speed (time_scale), and pause state."""
        return await handle_get_play_state(active_client, params)

    @server.tool(
        name="godot_set_play_state",
        annotations=ToolAnnotations(
            title="Set Play State & Simulation Speed",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def set_play_state(params: SetPlayStateInput) -> str:
        """Control pause state, simulation speed (Engine.time_scale), or step game physics/process frames."""
        return await handle_set_play_state(active_client, params)

    @server.tool(
        name="godot_cast_ray_3d",
        annotations=ToolAnnotations(
            title="Cast 3D Physics Ray",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def cast_ray_3d(params: CastRay3DInput) -> str:
        """Query 3D physics world by casting a ray from start to target position with collision layer masks and exclude lists."""
        return await handle_cast_ray_3d(active_client, params)

    @server.tool(
        name="godot_cast_shape_3d",
        annotations=ToolAnnotations(
            title="Cast 3D Physics Shape",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def cast_shape_3d(params: CastShape3DInput) -> str:
        """Query 3D physics world with a shape volume (Sphere, Box, Capsule, Cylinder) overlap or motion sweep."""
        return await handle_cast_shape_3d(active_client, params)

    @server.tool(
        name="godot_get_body_physics_state_3d",
        annotations=ToolAnnotations(
            title="Get 3D Body Physics State",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def get_body_physics_state_3d(params: GetBodyPhysicsState3DInput) -> str:
        """Retrieve live physics body telemetry (linear/angular velocities, mass, sleeping, contacts, collision layers)."""
        return await handle_get_body_physics_state_3d(active_client, params)

    @server.tool(
        name="godot_set_physics_debug_mode",
        annotations=ToolAnnotations(
            title="Set Physics Debug Visualization",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def set_physics_debug_mode(params: SetPhysicsDebugModeInput) -> str:
        """Toggle visible collision wireframe shapes, paths, and navigation meshes in editor / runtime preview."""
        return await handle_set_physics_debug_mode(active_client, params)

    @server.tool(
        name="godot_get_input_actions",
        annotations=ToolAnnotations(
            title="Get Input Actions",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def get_input_actions(params: GetInputActionsInput) -> str:
        """Query project input actions and bound triggers (Keys, Mouse, Gamepad buttons/axes)."""
        return await handle_get_input_actions(active_client, params)

    @server.tool(
        name="godot_configure_input_action",
        annotations=ToolAnnotations(
            title="Configure Input Action",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def configure_input_action(params: ConfigureInputActionInput) -> str:
        """Create or configure an input action with key/mouse/gamepad bindings and save into project.godot."""
        return await handle_configure_input_action(active_client, params)

    @server.tool(
        name="godot_configure_environment",
        annotations=ToolAnnotations(
            title="Configure WorldEnvironment & Post-Processing",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def configure_environment(params: ConfigureEnvironmentInput) -> str:
        """Configure post-processing (tonemap, glow, SSAO, SSIL, SSR, volumetric fog, skybox) in Environment resource or WorldEnvironment node."""
        return await handle_configure_environment(active_client, params)

    @server.tool(
        name="godot_set_editor_selection",
        annotations=ToolAnnotations(
            title="Set Editor Scene Selection",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def set_editor_selection(params: SetEditorSelectionInput) -> str:
        """Select nodes in the Godot Scene dock."""
        return await handle_set_editor_selection(active_client, params)

    @server.tool(
        name="godot_focus_node",
        annotations=ToolAnnotations(
            title="Focus Node in Inspector & Viewport",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def focus_node(params: FocusNodeInput) -> str:
        """Focus a node in the Inspector and switch to active 2D/3D viewport workspace."""
        return await handle_focus_node(active_client, params)

    @server.tool(
        name="godot_instantiate_model",
        annotations=ToolAnnotations(
            title="Instantiate 3D Model Asset",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def instantiate_model(params: InstantiateModelInput) -> str:
        """Instantiate a 3D model asset (.glb, .gltf, .blend) into the scene with transform and collision generation."""
        return await handle_instantiate_model(active_client, params)

    @server.tool(
        name="godot_configure_gltf_import",
        annotations=ToolAnnotations(
            title="Configure GLTF/3D Model Import",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def configure_gltf_import(params: ConfigureGLTFImportInput) -> str:
        """Configure .import settings for a 3D model (LODs, shadow meshes, skeleton bones, material extraction) and reimport."""
        return await handle_configure_gltf_import(active_client, params)

    @server.tool(
        name="godot_configure_particles",
        annotations=ToolAnnotations(
            title="Configure VFX Particles",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def configure_particles(params: ConfigureParticlesInput) -> str:
        """Create or configure a GPUParticles3D/2D or CPUParticles system and ParticleProcessMaterial resource."""
        return await handle_configure_particles(active_client, params)

    @server.tool(
        name="godot_get_export_presets",
        annotations=ToolAnnotations(
            title="Get Export Presets",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def get_export_presets(params: GetExportPresetsInput) -> str:
        """Query all build presets and platforms configured in export_presets.cfg."""
        return await handle_get_export_presets(active_client, params)

    @server.tool(
        name="godot_export_project",
        annotations=ToolAnnotations(
            title="Export Project Build",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def export_project(params: ExportProjectInput) -> str:
        """Export project binary headlessly for specified preset target."""
        return await handle_export_project(active_client, params)

    @server.tool(
        name="godot_get_autoloads",
        annotations=ToolAnnotations(
            title="Get Autoload Singletons",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def get_autoloads(params: GetAutoloadsInput) -> str:
        """Query all global autoload singletons configured in project.godot."""
        return await handle_get_autoloads(active_client, params)

    @server.tool(
        name="godot_set_autoload",
        annotations=ToolAnnotations(
            title="Configure Autoload Singleton",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def set_autoload(params: SetAutoloadInput) -> str:
        """Add, update, remove, or toggle autoload singletons in project.godot."""
        return await handle_set_autoload(active_client, params)

    @server.tool(
        name="godot_get_node_signals",
        annotations=ToolAnnotations(
            title="Get Node Signals",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def get_node_signals(params: GetNodeSignalsInput) -> str:
        """Introspect all signals and argument definitions on a node in the active scene."""
        return await handle_get_node_signals(active_client, params)

    @server.tool(
        name="godot_get_signal_connections",
        annotations=ToolAnnotations(
            title="Get Signal Connections",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def get_signal_connections(params: GetSignalConnectionsInput) -> str:
        """Query incoming and outgoing signal connection graphs for a target node."""
        return await handle_get_signal_connections(active_client, params)

    @server.tool(
        name="godot_evaluate_expression",
        annotations=ToolAnnotations(
            title="Evaluate GDScript Expression",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def evaluate_expression(params: EvaluateExpressionInput) -> str:
        """Safely parse and evaluate runtime GDScript math, logical expressions, or method calls."""
        return await handle_evaluate_expression(active_client, params)

    @server.tool(
        name="godot_create_shader",
        annotations=ToolAnnotations(
            title="Create Custom Shader",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def create_shader(params: CreateShaderInput) -> str:
        """Create a custom Godot .gdshader file and matching ShaderMaterial."""
        return await handle_create_shader(active_client, params)

    @server.tool(
        name="godot_set_shader_param",
        annotations=ToolAnnotations(
            title="Set Shader Parameter",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def set_shader_param(params: SetShaderParamInput) -> str:
        """Inspect and live-update a uniform parameter on a ShaderMaterial."""
        return await handle_set_shader_param(active_client, params)

    @server.tool(
        name="godot_configure_animation_tree",
        annotations=ToolAnnotations(
            title="Configure AnimationTree",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def configure_animation_tree(params: ConfigureAnimationTreeInput) -> str:
        """Create or configure an AnimationTree node, state machine graph, and transition conditions."""
        return await handle_configure_animation_tree(active_client, params)

    @server.tool(
        name="godot_get_translations",
        annotations=ToolAnnotations(
            title="Get Translations",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def get_translations(params: GetTranslationsInput) -> str:
        """Query translation tables and active locales configured in ProjectSettings."""
        return await handle_get_translations(active_client, params)

    @server.tool(
        name="godot_add_translation",
        annotations=ToolAnnotations(
            title="Add Translation",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def add_translation(params: AddTranslationInput) -> str:
        """Register a translation file (.csv, .po, .translation) in ProjectSettings."""
        return await handle_add_translation(active_client, params)

    @server.tool(
        name="godot_get_uid",
        annotations=ToolAnnotations(
            title="Get Resource UID",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def get_uid(params: GetUIDInput) -> str:
        """Convert a resource path into its native Godot uid:// identifier string."""
        return await handle_get_uid(active_client, params)

    @server.tool(
        name="godot_resolve_uid",
        annotations=ToolAnnotations(
            title="Resolve Resource UID",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def resolve_uid(params: ResolveUIDInput) -> str:
        """Resolve a uid:// identifier back into its current project file path."""
        return await handle_resolve_uid(active_client, params)

    @server.tool(
        name="godot_get_dependencies",
        annotations=ToolAnnotations(
            title="Get Dependencies",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def get_dependencies(params: GetDependenciesInput) -> str:
        """Query the dependency list for a scene, resource, or script."""
        return await handle_get_dependencies(active_client, params)

    @server.tool(
        name="godot_get_plugins",
        annotations=ToolAnnotations(
            title="Get Editor Plugins",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def get_plugins(params: GetPluginsInput) -> str:
        """Discover installed editor plugins in res://addons/ and inspect active status."""
        return await handle_get_plugins(active_client, params)

    @server.tool(
        name="godot_set_plugin_status",
        annotations=ToolAnnotations(
            title="Set Plugin Status",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def set_plugin_status(params: SetPluginStatusInput) -> str:
        """Enable or disable an editor addon dynamically."""
        return await handle_set_plugin_status(active_client, params)

    @server.tool(
        name="godot_configure_navigation_obstacle",
        annotations=ToolAnnotations(
            title="Configure Navigation Obstacle",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def configure_navigation_obstacle(
        params: ConfigureNavigationObstacleInput,
    ) -> str:
        """Create or configure a NavigationObstacle2D/3D node with avoidance radius, velocity, or polygon vertices."""
        return await handle_configure_navigation_obstacle(active_client, params)

    @server.tool(
        name="godot_configure_tileset_terrain",
        annotations=ToolAnnotations(
            title="Configure TileSet Terrain",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def configure_tileset_terrain(
        params: ConfigureTileSetTerrainInput,
    ) -> str:
        """Create and configure TileSet terrain sets, terrain modes, and autotiling peering bit mappings."""
        return await handle_configure_tileset_terrain(active_client, params)

    @server.tool(
        name="godot_diff_scene",
        annotations=ToolAnnotations(
            title="Diff Scene Tree",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def diff_scene(params: DiffSceneInput) -> str:
        """Diff the live edited scene in memory against its saved .tscn file on disk, or compare two .tscn scene files."""
        return await handle_diff_scene(active_client, params)

    @server.tool(
        name="godot_undo",
        annotations=ToolAnnotations(
            title="Undo Action",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def undo_action(params: UndoInput) -> str:
        """Revert the last editor action on the active scene or global undo history."""
        return await handle_undo(active_client, params)

    @server.tool(
        name="godot_redo",
        annotations=ToolAnnotations(
            title="Redo Action",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def redo_action(params: RedoInput) -> str:
        """Redo the previously undone editor action on the active scene or global undo history."""
        return await handle_redo(active_client, params)

    @server.tool(
        name="godot_get_selected_nodes",
        annotations=ToolAnnotations(
            title="Get Selected Nodes",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def get_selected_nodes(params: GetSelectedNodesInput) -> str:
        """Query currently selected nodes in the Godot Editor SceneTree."""
        return await handle_get_selected_nodes(active_client, params)

    @server.tool(
        name="godot_set_selected_nodes",
        annotations=ToolAnnotations(
            title="Set Selected Nodes",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def set_selected_nodes(params: SetSelectedNodesInput) -> str:
        """Set active node selection in the Godot Editor SceneTree and optionally inspect the primary node."""
        return await handle_set_selected_nodes(active_client, params)

    @server.tool(
        name="godot_audit_assets",
        annotations=ToolAnnotations(
            title="Audit Project Assets",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def audit_assets(params: AuditAssetsInput) -> str:
        """Deep project-wide asset audit scanning for unreferenced orphan files and broken dependency references."""
        return await handle_audit_assets(active_client, params)

    @server.tool(
        name="godot_clean_orphans",
        annotations=ToolAnnotations(
            title="Clean Orphan Assets",
            read_only_hint=False,
            destructive_hint=True,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def clean_orphans(params: CleanOrphansInput) -> str:
        """Safely clean or quarantine unreferenced orphan files with dry-run verification."""
        return await handle_clean_orphans(active_client, params)

    @server.tool(
        name="godot_get_texture_info",
        annotations=ToolAnnotations(
            title="Get Texture Info",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def get_texture_info(params: GetTextureInfoInput) -> str:
        """Inspect dimensions, pixel format, mipmaps, and estimated VRAM footprint for a texture."""
        return await handle_get_texture_info(active_client, params)

    @server.tool(
        name="godot_run_gut_tests",
        annotations=ToolAnnotations(
            title="Run GUT Tests",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def run_gut_tests(params: RunGUTTestsInput) -> str:
        """Execute Godot Unit Test (GUT) suites or custom test runners headlessly with automated log parsing."""
        return await handle_run_gut_tests(active_client, params)

    @server.tool(
        name="godot_generate_gut_test",
        annotations=ToolAnnotations(
            title="Generate GUT Test",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def generate_gut_test(params: GenerateGUTTestInput) -> str:
        """Scaffold a complete GUT test script inheriting GutTest for target GDScript scripts or scenes."""
        return await handle_generate_gut_test(active_client, params)

    @server.tool(
        name="godot_get_editor_layout",
        annotations=ToolAnnotations(
            title="Get Editor Layout",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def get_editor_layout(params: GetEditorLayoutInput) -> str:
        """Query current Godot Editor workspace layout, active main screen, and open scene tabs."""
        return await handle_get_editor_layout(active_client, params)

    @server.tool(
        name="godot_set_editor_layout",
        annotations=ToolAnnotations(
            title="Set Editor Layout",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def set_editor_layout(params: SetEditorLayoutInput) -> str:
        """Configure Godot Editor workspace layout, main screen tabs, and distraction-free mode."""
        return await handle_set_editor_layout(active_client, params)

    @server.tool(
        name="godot_reparent_node",
        annotations=ToolAnnotations(
            title="Reparent Node",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def reparent_node(params: ReparentNodeInput) -> str:
        """Reparent a node to a new parent in the active scene tree while preserving global transform."""
        return await handle_reparent_node(active_client, params)

    @server.tool(
        name="godot_duplicate_node",
        annotations=ToolAnnotations(
            title="Duplicate Node",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def duplicate_node(params: DuplicateNodeInput) -> str:
        """Deep duplicate an existing node with flags for signals, groups, and scripts."""
        return await handle_duplicate_node(active_client, params)

    @server.tool(
        name="godot_set_node_owner",
        annotations=ToolAnnotations(
            title="Set Node Owner",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def set_node_owner(params: SetNodeOwnerInput) -> str:
        """Set the owner node of a target node or subtree for scene file persistence."""
        return await handle_set_node_owner(active_client, params)

    @server.tool(
        name="godot_attach_script",
        annotations=ToolAnnotations(
            title="Attach Script",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def attach_script(params: AttachScriptInput) -> str:
        """Attach a script file (.gd/.cs) to a live node or detach existing script."""
        return await handle_attach_script(active_client, params)

    @server.tool(
        name="godot_reload_scripts",
        annotations=ToolAnnotations(
            title="Reload Scripts",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def reload_scripts(params: ReloadScriptsInput) -> str:
        """Force reload GDScript resources in memory cache without restarting the editor."""
        return await handle_reload_scripts(active_client, params)

    @server.tool(
        name="godot_get_node_script_info",
        annotations=ToolAnnotations(
            title="Get Node Script Info",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def get_node_script_info(params: GetNodeScriptInfoInput) -> str:
        """Inspect attached script methods, signals, constants, and exported properties with default vs current values."""
        return await handle_get_node_script_info(active_client, params)

    @server.tool(
        name="godot_configure_camera",
        annotations=ToolAnnotations(
            title="Configure Camera",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def configure_camera(params: ConfigureCameraInput) -> str:
        """Configure Camera2D or Camera3D settings (projection, FOV, zoom, smoothing, clipping)."""
        return await handle_configure_camera(active_client, params)

    @server.tool(
        name="godot_configure_render_settings",
        annotations=ToolAnnotations(
            title="Configure Render Settings",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def configure_render_settings(params: ConfigureRenderSettingsInput) -> str:
        """Tune ProjectSettings rendering features (MSAA, FXAA, TAA, FSR scaling, shadow resolutions, V-Sync)."""
        return await handle_configure_render_settings(active_client, params)

    @server.tool(
        name="godot_capture_viewport",
        annotations=ToolAnnotations(
            title="Capture Viewport",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def capture_viewport(params: CaptureViewportInput) -> str:
        """Capture a high-resolution viewport frame with scaling and optional base64 image data for AI vision."""
        return await handle_capture_viewport(active_client, params)

    @server.tool(
        name="godot_simulate_input",
        annotations=ToolAnnotations(
            title="Simulate Input",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def simulate_input(params: SimulateInputInput) -> str:
        """Simulate low-level keyboard, mouse, action, and joypad input events in the running game or editor."""
        return await handle_simulate_input(active_client, params)

    @server.tool(
        name="godot_draw_debug_shapes",
        annotations=ToolAnnotations(
            title="Draw Debug Shapes",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def draw_debug_shapes(params: DrawDebugShapesInput) -> str:
        """Render temporary 2D or 3D debug shapes (lines, rays, boxes, spheres, circles, text) with auto-expiration."""
        return await handle_draw_debug_shapes(active_client, params)

    @server.tool(
        name="godot_clear_debug_shapes",
        annotations=ToolAnnotations(
            title="Clear Debug Shapes",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def clear_debug_shapes(params: ClearDebugShapesInput) -> str:
        """Clear active debug shape overlays from the viewport."""
        return await handle_clear_debug_shapes(active_client, params)

    @server.tool(
        name="godot_find_elements",
        annotations=ToolAnnotations(
            title="Find Elements",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def find_elements(params: FindElementsInput) -> str:
        """Find scene and UI elements matching selectors (text, role, type, name, group, path) for autonomous E2E testing."""
        return await handle_find_elements(active_client, params)

    @server.tool(
        name="godot_interact_node",
        annotations=ToolAnnotations(
            title="Interact Node",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def interact_node(params: InteractNodeInput) -> str:
        """Execute Playwright-like interaction primitives on scene nodes (click, type_text, focus, hover, scroll)."""
        return await handle_interact_node(active_client, params)

    @server.tool(
        name="godot_wait_for_condition",
        annotations=ToolAnnotations(
            title="Wait For Condition",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def wait_for_condition(params: WaitForConditionInput) -> str:
        """Wait for runtime state conditions (node existence, visibility, property values, expressions) with timeout."""
        return await handle_wait_for_condition(active_client, params)

    @server.tool(
        name="godot_assert_node_state",
        annotations=ToolAnnotations(
            title="Assert Node State",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def assert_node_state(params: AssertNodeStateInput) -> str:
        """Assert multiple expected properties and states against a scene node for autonomous verification."""
        return await handle_assert_node_state(active_client, params)

    @server.tool(
        name="godot_configure_gridmap",
        annotations=ToolAnnotations(
            title="Configure GridMap",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def configure_gridmap(params: ConfigureGridMapInput) -> str:
        """Batch place, clear, and configure 3D voxel cells on GridMap nodes."""
        return await handle_configure_gridmap(active_client, params)

    @server.tool(
        name="godot_create_curve_path",
        annotations=ToolAnnotations(
            title="Create Curve Path",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def create_curve_path(params: CreateCurvePathInput) -> str:
        """Create 2D or 3D Bezier curve paths (Path2D/Path3D) with handles, tilt, and PathFollow attachment."""
        return await handle_create_curve_path(active_client, params)

    @server.tool(
        name="godot_audit_orphan_nodes",
        annotations=ToolAnnotations(
            title="Audit Orphan Nodes",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def audit_orphan_nodes(params: AuditOrphanNodesInput) -> str:
        """Audit unparented orphan nodes in engine memory to detect leaks."""
        return await handle_audit_orphan_nodes(active_client, params)

    @server.tool(
        name="godot_capture_profiler_trace",
        annotations=ToolAnnotations(
            title="Capture Profiler Trace",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def capture_profiler_trace(params: CaptureProfilerTraceInput) -> str:
        """Sample multi-frame CPU/GPU execution times, draw calls, and memory telemetry."""
        return await handle_capture_profiler_trace(active_client, params)

    @server.tool(
        name="godot_inspect_vram_usage",
        annotations=ToolAnnotations(
            title="Inspect VRAM Usage",
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def inspect_vram_usage(params: InspectVRAMUsageInput) -> str:
        """Inspect GPU video memory allocation breakdowns across textures and buffers."""
        return await handle_inspect_vram_usage(active_client, params)

    @server.tool(
        name="godot_configure_multiplayer_spawner",
        annotations=ToolAnnotations(
            title="Configure Multiplayer Spawner",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def configure_multiplayer_spawner(
        params: ConfigureMultiplayerSpawnerInput,
    ) -> str:
        """Configure MultiplayerSpawner auto-spawn paths, spawn limits, and spawnable scenes."""
        return await handle_configure_multiplayer_spawner(active_client, params)

    @server.tool(
        name="godot_configure_multiplayer_synchronizer",
        annotations=ToolAnnotations(
            title="Configure Multiplayer Synchronizer",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=False,
            open_world_hint=False,
        ),
    )
    async def configure_multiplayer_synchronizer(
        params: ConfigureMultiplayerSynchronizerInput,
    ) -> str:
        """Configure MultiplayerSynchronizer property replication configs, sync intervals, and visibility."""
        return await handle_configure_multiplayer_synchronizer(active_client, params)

    @server.tool(
        name="godot_simulate_network_conditions",
        annotations=ToolAnnotations(
            title="Simulate Network Conditions",
            read_only_hint=False,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        ),
    )
    async def simulate_network_conditions(
        params: SimulateNetworkConditionsInput,
    ) -> str:
        """Simulate network latency, packet loss, jitter, or offline mode for multiplayer testing."""
        return await handle_simulate_network_conditions(active_client, params)

    # --- Dynamic MCP Resources (godot://) ---

    @server.resource("godot://audio/layout")
    async def resource_audio_layout() -> str:
        """Dynamic MCP resource providing current AudioServer bus hierarchy and effect chains JSON."""
        res = await active_client.get_audio_layout(include_effects=True)
        return json.dumps(res.data, indent=2)

    @server.resource("godot://performance/metrics")
    async def resource_performance_metrics() -> str:
        """Dynamic MCP resource providing real-time Godot performance telemetry JSON."""
        res = await active_client.get_performance_metrics()
        return json.dumps(res.data, indent=2)

    @server.resource("godot://project/settings")
    async def resource_project_settings() -> str:
        """Dynamic MCP resource providing full project settings JSON."""
        res = await active_client.get_project_settings()
        return json.dumps(res.data, indent=2)

    @server.resource("godot://scene/active/tree")
    async def resource_active_scene_tree() -> str:
        """Dynamic MCP resource providing live node hierarchy of the active scene."""
        res = await active_client.list_nodes()
        return json.dumps(res.data, indent=2)

    @server.resource("godot://engine/classes/{class_name}")
    async def resource_engine_class_info(class_name: str) -> str:
        """Dynamic MCP resource template providing ClassDB property, method, signal, and enum reflection for any Godot class."""
        res = await active_client.get_class_info(class_name)
        return json.dumps(res.data, indent=2)

    @server.resource("godot://logs/editor.log")
    async def resource_editor_log() -> str:
        """Dynamic MCP resource providing recent Godot engine/editor log output."""
        return "Godot MCP Live Bridge active and listening on port 3118."

    # --- Standard Workflow Prompts (prompt://) ---

    @server.prompt("fix_scene_warnings")
    def prompt_fix_scene_warnings() -> str:
        """Guided workflow for inspecting active nodes and automatically clearing configuration warnings."""
        return (
            "Analyze the active Godot scene for node configuration warnings.\n"
            "1. Run `godot_list_nodes` to inspect all nodes in the scene tree.\n"
            "2. Identify any nodes with missing collision shapes (e.g. CollisionObject2D/3D without CollisionShape), "
            "missing textures, or unset required properties.\n"
            "3. Use `godot_create_node` and `godot_modify_node` to supply required child nodes or shapes with non-empty extents/radius.\n"
            "4. Verify the scene has 0 warnings and save with `godot_save_scene`."
        )

    @server.prompt("create_rich_ui")
    def prompt_create_rich_ui() -> str:
        """Guided workflow for constructing responsive, themed Godot 4 GUI layouts."""
        return (
            "Build a responsive, modern GUI in Godot 4 using Control nodes and theme containers:\n"
            "1. If creating a standalone interface, use `godot_create_scene` with root type 'Control' or 'CanvasLayer'.\n"
            "2. Lay out UI regions using MarginContainer, VBoxContainer, HBoxContainer, and PanelContainer.\n"
            "3. Set size flags (`size_flags_horizontal = 3`, `size_flags_vertical = 3`) for expandable components.\n"
            "4. Add Buttons, Labels, ProgressBars, LineEdits, and TabContainers with proper styling.\n"
            "5. Wire up interactive signals using `godot_connect_signal`."
        )

    @server.prompt("scaffold_character")
    def prompt_scaffold_character() -> str:
        """Guided workflow for setting up a 2D or 3D character controller."""
        return (
            "Scaffold a complete character controller in Godot 4:\n"
            "1. Create the root node as 'CharacterBody2D' (or 'CharacterBody3D') using `godot_create_scene` or `godot_create_node`.\n"
            "2. Add a 'CollisionShape2D' (or 'CollisionShape3D') child with an attached Shape resource.\n"
            "3. Add a visual component ('Sprite2D', 'AnimatedSprite2D', or 'MeshInstance3D').\n"
            "4. Attach a movement script with `godot_create_script` implementing gravity, jump, velocity calculation, and `move_and_slide()`.\n"
            "5. Validate the script with `godot_validate_script` and save the scene."
        )

    return server


# Default server instance for direct module execution
mcp = create_server()
