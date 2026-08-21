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
from godot_mcp.models.audio import (
    ConfigureAudioBusInput,
    GetAudioLayoutInput,
    SetBusEffectInput,
)
from godot_mcp.models.autoload import (
    GetAutoloadsInput,
    SetAutoloadInput,
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
from godot_mcp.models.editor_focus import (
    FocusNodeInput,
    SetEditorSelectionInput,
)
from godot_mcp.models.environment import ConfigureEnvironmentInput
from godot_mcp.models.export_build import (
    ExportProjectInput,
    GetExportPresetsInput,
)
from godot_mcp.models.input_map import (
    ConfigureInputActionInput,
    GetInputActionsInput,
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
from godot_mcp.models.script import (
    CreateScriptInput,
    ValidateScriptInput,
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
from godot_mcp.tools.anim_tree_tools import handle_configure_animation_tree
from godot_mcp.tools.animation_tools import handle_create_animation
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
from godot_mcp.tools.dcc_tools import (
    handle_configure_gltf_import,
    handle_instantiate_model,
)
from godot_mcp.tools.debug_tools import (
    handle_run_project,
    handle_run_tests,
    handle_take_screenshot,
)
from godot_mcp.tools.editor_tools import (
    handle_focus_node,
    handle_set_editor_selection,
)
from godot_mcp.tools.environment_tools import handle_configure_environment
from godot_mcp.tools.eval_tools import handle_evaluate_expression
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
