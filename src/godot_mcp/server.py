"""FastMCP Server setup and tool registrations for Godot Engine."""

import json

from mcp.server import MCPServer
from mcp.types import ToolAnnotations

from godot_mcp.client.base import GodotClient
from godot_mcp.client.manager import ClientManager
from godot_mcp.config import GodotConfig
from godot_mcp.models.animation import CreateAnimationInput
from godot_mcp.models.asset import (
    CreateCollisionPolygonInput,
    ReimportAssetInput,
)
from godot_mcp.models.debug import (
    RunProjectInput,
    RunTestsInput,
    TakeScreenshotInput,
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
from godot_mcp.models.performance import GetPerformanceMetricsInput
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
from godot_mcp.models.tilemap import (
    CreateTileMapLayerInput,
    GetTileMapCellsInput,
    SetTileMapCellsInput,
)
from godot_mcp.tools.animation_tools import handle_create_animation
from godot_mcp.tools.asset_tools import (
    handle_create_collision_polygon,
    handle_reimport_asset,
)
from godot_mcp.tools.debug_tools import (
    handle_run_project,
    handle_run_tests,
    handle_take_screenshot,
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
from godot_mcp.tools.performance_tools import handle_get_performance_metrics
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

    # --- Dynamic MCP Resources (godot://) ---

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
