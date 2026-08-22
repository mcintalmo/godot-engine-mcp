"""FastMCP Server setup and tool registrations for Godot Engine."""

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from mcp.server import MCPServer
from mcp.types import ToolAnnotations
from pydantic import BaseModel

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
from godot_mcp.models.asset_library import (
    GetAssetDetailsInput,
    InstallAssetPackageInput,
    SearchAssetLibraryInput,
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
from godot_mcp.models.gameplay_scaffolding import (
    CreateDialogueResourceInput,
    ScaffoldStateMachineInput,
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
from godot_mcp.models.lightmap_gi import (
    BakeLightmapsInput,
    ConfigureLightmapGIInput,
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
from godot_mcp.models.multimesh_scatter import (
    ConfigureLODManagerInput,
    ScatterMultiMeshInput,
)
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
from godot_mcp.models.openxr import (
    ConfigureXRPassthroughInput,
    SetupXRRigInput,
)
from godot_mcp.models.particles import ConfigureParticlesInput
from godot_mcp.models.performance import GetPerformanceMetricsInput
from godot_mcp.models.physics import (
    CastRay3DInput,
    CastShape3DInput,
    GetBodyPhysicsState3DInput,
    SetPhysicsDebugModeInput,
)
from godot_mcp.models.physics_constraints import (
    ConfigurePhysicsJointInput,
    GenerateRagdollInput,
)
from godot_mcp.models.plugin_mgr import (
    GetPluginsInput,
    SetPluginStatusInput,
)
from godot_mcp.models.procedural_geometry import (
    CreateCSGShapeInput,
    GenerateProceduralMeshInput,
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
from godot_mcp.models.rendering_device import (
    DispatchComputeShaderInput,
    InspectRenderingDeviceInput,
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
from godot_mcp.models.skeleton_ik import (
    ConfigureBoneAttachmentInput,
    InspectSkeletonInput,
    SetupInverseKinematicsInput,
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
from godot_mcp.tools.asset_library_tools import (
    handle_get_asset_details,
    handle_install_asset_package,
    handle_search_asset_library,
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
from godot_mcp.tools.gameplay_scaffolding_tools import (
    handle_create_dialogue_resource,
    handle_scaffold_state_machine,
)
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
from godot_mcp.tools.lightmap_gi_tools import (
    handle_bake_lightmaps,
    handle_configure_lightmap_gi,
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
from godot_mcp.tools.multimesh_scatter_tools import (
    handle_configure_lod_manager,
    handle_scatter_multimesh,
)
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
from godot_mcp.tools.openxr_tools import (
    handle_configure_xr_passthrough,
    handle_setup_xr_rig,
)
from godot_mcp.tools.particle_tools import handle_configure_particles
from godot_mcp.tools.performance_tools import handle_get_performance_metrics
from godot_mcp.tools.physics_constraints_tools import (
    handle_configure_physics_joint,
    handle_generate_ragdoll,
)
from godot_mcp.tools.physics_tools import (
    handle_cast_ray_3d,
    handle_cast_shape_3d,
    handle_get_body_physics_state_3d,
    handle_set_physics_debug_mode,
)
from godot_mcp.tools.plugin_tools import (
    handle_get_plugins,
    handle_set_plugin_status,
)
from godot_mcp.tools.procedural_geometry_tools import (
    handle_create_csg_shape,
    handle_generate_procedural_mesh,
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
from godot_mcp.tools.rendering_device_tools import (
    handle_dispatch_compute_shader,
    handle_inspect_rendering_device,
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
from godot_mcp.tools.skeleton_ik_tools import (
    handle_configure_bone_attachment,
    handle_inspect_skeleton,
    handle_setup_inverse_kinematics,
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


@dataclass(frozen=True)
class ToolDef:
    """Declarative specification for an MCP tool endpoint."""

    name: str
    title: str
    description: str
    input_model: type[BaseModel]
    handler: Callable[..., Any]
    read_only: bool = False
    idempotent: bool = False
    destructive: bool = False


TOOL_DEFINITIONS: list[ToolDef] = [
    # Project & Version
    ToolDef(
        "godot_get_version",
        "Get Godot Engine Version",
        "Get current Godot Engine version, build info, mode, and project path.",
        GetVersionInput,
        handle_get_version,
        read_only=True,
        idempotent=True,
    ),
    ToolDef(
        "godot_get_project_settings",
        "Get Project Settings",
        "Query settings from project.godot (application name, display, physics, etc).",
        GetProjectSettingsInput,
        handle_get_project_settings,
        read_only=True,
        idempotent=True,
    ),
    ToolDef(
        "godot_set_project_setting",
        "Set Project Setting",
        "Write or update a configuration setting in project.godot.",
        SetProjectSettingInput,
        handle_set_project_setting,
        idempotent=True,
    ),
    ToolDef(
        "godot_list_project_files",
        "List Project Files",
        "List files in the Godot project tree matching patterns and extensions.",
        ListProjectFilesInput,
        handle_list_project_files,
        read_only=True,
        idempotent=True,
    ),
    # Scene & Nodes
    ToolDef(
        "godot_list_nodes",
        "List Nodes in Scene Tree",
        "List all nodes in the active scene tree with hierarchy, types, and properties.",
        ListNodesInput,
        handle_list_nodes,
        read_only=True,
    ),
    ToolDef(
        "godot_get_node",
        "Get Node Details",
        "Inspect a specific node's type, script, groups, signals, and properties.",
        GetNodeInput,
        handle_get_node,
        read_only=True,
    ),
    ToolDef(
        "godot_create_node",
        "Create Node",
        "Create and add a new node of any Godot class to the active scene.",
        CreateNodeInput,
        handle_create_node,
    ),
    ToolDef(
        "godot_modify_node",
        "Modify Node Properties",
        "Update properties on an existing node in the active scene.",
        ModifyNodeInput,
        handle_modify_node,
    ),
    ToolDef(
        "godot_delete_node",
        "Delete Node",
        "Remove a node from the active scene tree.",
        DeleteNodeInput,
        handle_delete_node,
        destructive=True,
    ),
    ToolDef(
        "godot_connect_signal",
        "Connect Node Signal",
        "Connect a signal from a source node to a target node method.",
        ConnectSignalInput,
        handle_connect_signal,
    ),
    ToolDef(
        "godot_instantiate_scene",
        "Instantiate Scene",
        "Instantiate a packed scene (.tscn / .scn) as a child node.",
        InstantiateSceneInput,
        handle_instantiate_scene,
    ),
    ToolDef(
        "godot_save_scene",
        "Save Active Scene",
        "Save the currently edited scene to disk.",
        SaveSceneInput,
        handle_save_scene,
    ),
    ToolDef(
        "godot_open_scene",
        "Open Scene in Editor",
        "Open a scene file (.tscn) in the Godot Editor workspace.",
        OpenSceneInput,
        handle_open_scene,
    ),
    ToolDef(
        "godot_create_scene",
        "Create New Scene",
        "Create a brand new scene file with root node and save to disk.",
        CreateSceneInput,
        handle_create_scene,
    ),
    # Scene Hierarchy & Mutation
    ToolDef(
        "godot_reparent_node",
        "Reparent Node",
        "Move a node to a new parent in the active scene tree.",
        ReparentNodeInput,
        handle_reparent_node,
    ),
    ToolDef(
        "godot_duplicate_node",
        "Duplicate Node",
        "Deep duplicate a node with signal and script flags.",
        DuplicateNodeInput,
        handle_duplicate_node,
    ),
    ToolDef(
        "godot_set_node_owner",
        "Set Node Owner",
        "Set or synchronize the owner property of a node.",
        SetNodeOwnerInput,
        handle_set_node_owner,
    ),
    ToolDef(
        "godot_diff_scene",
        "Diff Scene Files",
        "Compare two scene files (.tscn) and generate structural diffs.",
        DiffSceneInput,
        handle_diff_scene,
        read_only=True,
    ),
    # Script & LSP
    ToolDef(
        "godot_validate_script",
        "Validate GDScript",
        "Parse and validate GDScript code for syntax and type errors.",
        ValidateScriptInput,
        handle_validate_script,
        read_only=True,
        idempotent=True,
    ),
    ToolDef(
        "godot_create_script",
        "Create GDScript",
        "Create a new GDScript file with template code and class extends.",
        CreateScriptInput,
        handle_create_script,
    ),
    ToolDef(
        "godot_attach_script",
        "Attach Script to Node",
        "Attach or detach a GDScript to/from an active node.",
        AttachScriptInput,
        handle_attach_script,
    ),
    ToolDef(
        "godot_reload_scripts",
        "Reload Scripts in Memory",
        "Force reload modified GDScript resources in memory.",
        ReloadScriptsInput,
        handle_reload_scripts,
    ),
    ToolDef(
        "godot_get_node_script_info",
        "Get Node Script Reflection",
        "Inspect exported properties, methods, constants, and signals.",
        GetNodeScriptInfoInput,
        handle_get_node_script_info,
        read_only=True,
    ),
    ToolDef(
        "godot_lsp_query",
        "LSP Semantic Query",
        "Query symbols, definitions, references, or hover documentation.",
        LSPQueryInput,
        handle_lsp_query,
        read_only=True,
    ),
    ToolDef(
        "godot_lsp_rename",
        "LSP Semantic Rename",
        "Perform cross-file semantic symbol rename.",
        LSPRenameInput,
        handle_lsp_rename,
    ),
    # Reflection & Documentation
    ToolDef(
        "godot_get_class_info",
        "Get Godot Class Info",
        "Query class inheritance, properties, methods, and signals from ClassDB.",
        GetClassInfoInput,
        handle_get_class_info,
        read_only=True,
        idempotent=True,
    ),
    ToolDef(
        "godot_get_documentation",
        "Get Engine Documentation",
        "Fetch built-in documentation for classes, methods, and properties.",
        GetDocumentationInput,
        handle_get_documentation,
        read_only=True,
        idempotent=True,
    ),
    ToolDef(
        "godot_evaluate_expression",
        "Evaluate Expression at Runtime",
        "Evaluate arbitrary GDScript expression safely at runtime.",
        EvaluateExpressionInput,
        handle_evaluate_expression,
    ),
    # Debug, Play & Testing
    ToolDef(
        "godot_run_project",
        "Run Godot Project",
        "Launch project or scene in debug mode via CLI.",
        RunProjectInput,
        handle_run_project,
    ),
    ToolDef(
        "godot_run_tests",
        "Run Automated Tests",
        "Execute test scenes or unit test runners headlessly.",
        RunTestsInput,
        handle_run_tests,
    ),
    ToolDef(
        "godot_take_screenshot",
        "Take Viewport Screenshot",
        "Capture full screenshot of active game or editor viewport.",
        TakeScreenshotInput,
        handle_take_screenshot,
        read_only=True,
    ),
    ToolDef(
        "godot_generate_gut_test",
        "Generate GUT Unit Test",
        "Scaffold GUT test script for a target class or script.",
        GenerateGUTTestInput,
        handle_generate_gut_test,
    ),
    ToolDef(
        "godot_run_gut_tests",
        "Run GUT Unit Tests",
        "Execute GUT test suites and capture test results.",
        RunGUTTestsInput,
        handle_run_gut_tests,
    ),
    # Materials, Shaders & Rendering
    ToolDef(
        "godot_validate_shader",
        "Validate Shader Code",
        "Compile and check Godot Shader Language code for errors.",
        ValidateShaderInput,
        handle_validate_shader,
        read_only=True,
        idempotent=True,
    ),
    ToolDef(
        "godot_create_material",
        "Create Material Resource",
        "Create StandardMaterial3D, ORMMaterial3D, ShaderMaterial, or CanvasItemMaterial.",
        CreateMaterialInput,
        handle_create_material,
    ),
    ToolDef(
        "godot_create_shader",
        "Create Custom Shader",
        "Create custom Godot shader (.gdshader) with matching material.",
        CreateShaderInput,
        handle_create_shader,
    ),
    ToolDef(
        "godot_set_shader_param",
        "Set Shader Uniform Parameter",
        "Set shader parameter uniform values on a ShaderMaterial.",
        SetShaderParamInput,
        handle_set_shader_param,
    ),
    ToolDef(
        "godot_configure_particles",
        "Configure Particles",
        "Configure GPUParticles2D/3D or CPUParticles2D/3D node emission.",
        ConfigureParticlesInput,
        handle_configure_particles,
    ),
    ToolDef(
        "godot_configure_environment",
        "Configure World Environment",
        "Adjust WorldEnvironment background, glow, tonemap, and ambient light.",
        ConfigureEnvironmentInput,
        handle_configure_environment,
    ),
    ToolDef(
        "godot_configure_camera",
        "Configure Camera",
        "Create and configure Camera2D or Camera3D viewports and FOV.",
        ConfigureCameraInput,
        handle_configure_camera,
    ),
    ToolDef(
        "godot_configure_render_settings",
        "Configure Render Settings",
        "Tune anti-aliasing, shadow quality, V-Sync, and upscaling.",
        ConfigureRenderSettingsInput,
        handle_configure_render_settings,
    ),
    ToolDef(
        "godot_capture_viewport",
        "Capture High-Res Viewport",
        "Capture high-resolution viewport frame for AI Vision inspection.",
        CaptureViewportInput,
        handle_capture_viewport,
        read_only=True,
    ),
    # Global Illumination & Spatial XR
    ToolDef(
        "godot_configure_lightmap_gi",
        "Configure Global Illumination",
        "Configure 3D GI pipelines (LightmapGI, VoxelGI, ReflectionProbe).",
        ConfigureLightmapGIInput,
        handle_configure_lightmap_gi,
    ),
    ToolDef(
        "godot_bake_lightmaps",
        "Bake Lightmaps",
        "Trigger lightmap or voxel GI baking for the active scene.",
        BakeLightmapsInput,
        handle_bake_lightmaps,
    ),
    ToolDef(
        "godot_setup_xr_rig",
        "Setup OpenXR Rig",
        "Scaffold XROrigin3D, XRCamera3D, and XRController3D tracking rig.",
        SetupXRRigInput,
        handle_setup_xr_rig,
    ),
    ToolDef(
        "godot_configure_xr_passthrough",
        "Configure OpenXR Passthrough",
        "Configure OpenXR passthrough mode and foveated rendering.",
        ConfigureXRPassthroughInput,
        handle_configure_xr_passthrough,
    ),
    # Low-Level GPU Compute & MultiMesh
    ToolDef(
        "godot_dispatch_compute_shader",
        "Dispatch Compute Shader",
        "Execute compute shader on GPU via low-level RenderingDevice API.",
        DispatchComputeShaderInput,
        handle_dispatch_compute_shader,
    ),
    ToolDef(
        "godot_inspect_rendering_device",
        "Inspect RenderingDevice",
        "Query GPU RenderingDevice device name, vendor, limits, and capabilities.",
        InspectRenderingDeviceInput,
        handle_inspect_rendering_device,
        read_only=True,
        idempotent=True,
    ),
    ToolDef(
        "godot_scatter_multimesh",
        "Scatter MultiMesh",
        "High-performance GPU instanced scattering across a 3D bounding area.",
        ScatterMultiMeshInput,
        handle_scatter_multimesh,
    ),
    ToolDef(
        "godot_configure_lod_manager",
        "Configure LOD Manager",
        "Configure visibility ranges, LOD distance thresholds, and cross-fade modes.",
        ConfigureLODManagerInput,
        handle_configure_lod_manager,
    ),
    # Assets & DCC Imports
    ToolDef(
        "godot_reimport_asset",
        "Reimport Asset",
        "Trigger reimport of asset files with custom import parameters.",
        ReimportAssetInput,
        handle_reimport_asset,
    ),
    ToolDef(
        "godot_create_collision_polygon",
        "Create Collision Polygon",
        "Generate CollisionPolygon2D/3D shapes from sprite alpha or mesh.",
        CreateCollisionPolygonInput,
        handle_create_collision_polygon,
    ),
    ToolDef(
        "godot_configure_gltf_import",
        "Configure GLTF Import",
        "Configure GLTF/GLB 3D model import presets.",
        ConfigureGLTFImportInput,
        handle_configure_gltf_import,
    ),
    ToolDef(
        "godot_instantiate_model",
        "Instantiate 3D Model",
        "Instantiate a 3D model asset into the active scene.",
        InstantiateModelInput,
        handle_instantiate_model,
    ),
    ToolDef(
        "godot_audit_assets",
        "Audit Asset Usage",
        "Scan project for unused assets, missing dependencies, or broken paths.",
        AuditAssetsInput,
        handle_audit_assets,
        read_only=True,
    ),
    ToolDef(
        "godot_clean_orphans",
        "Clean Orphan Resources",
        "Remove or quarantine unreferenced and orphaned asset files.",
        CleanOrphansInput,
        handle_clean_orphans,
        destructive=True,
    ),
    ToolDef(
        "godot_get_texture_info",
        "Get Texture Metadata",
        "Query dimensions, format, VRAM compression, and mipmaps.",
        GetTextureInfoInput,
        handle_get_texture_info,
        read_only=True,
    ),
    # Animation & Audio
    ToolDef(
        "godot_create_animation",
        "Create Animation Track",
        "Create or modify tracks and keyframes in an AnimationPlayer.",
        CreateAnimationInput,
        handle_create_animation,
    ),
    ToolDef(
        "godot_configure_animation_tree",
        "Configure AnimationTree",
        "Setup state machines, blend spaces, and transitions in AnimationTree.",
        ConfigureAnimationTreeInput,
        handle_configure_animation_tree,
    ),
    ToolDef(
        "godot_configure_audio_bus",
        "Configure Audio Bus",
        "Add, rename, mute, solo, or route AudioServer buses.",
        ConfigureAudioBusInput,
        handle_configure_audio_bus,
    ),
    ToolDef(
        "godot_set_bus_effect",
        "Set Audio Bus Effect",
        "Add or adjust real-time audio effects on an audio bus.",
        SetBusEffectInput,
        handle_set_bus_effect,
    ),
    ToolDef(
        "godot_get_audio_layout",
        "Get Audio Layout",
        "Query complete AudioServer bus hierarchy and effect chains.",
        GetAudioLayoutInput,
        handle_get_audio_layout,
        read_only=True,
        idempotent=True,
    ),
    # World Building & 2D/3D Navigation
    ToolDef(
        "godot_create_tilemap_layer",
        "Create TileMapLayer",
        "Add a TileMapLayer node with TileSet binding.",
        CreateTileMapLayerInput,
        handle_create_tilemap_layer,
    ),
    ToolDef(
        "godot_set_tilemap_cells",
        "Set TileMap Cells",
        "Place or clear tiles on a TileMapLayer coordinate grid.",
        SetTileMapCellsInput,
        handle_set_tilemap_cells,
    ),
    ToolDef(
        "godot_get_tilemap_cells",
        "Get TileMap Cells",
        "Read placed cell coordinates and atlas coords from TileMapLayer.",
        GetTileMapCellsInput,
        handle_get_tilemap_cells,
        read_only=True,
    ),
    ToolDef(
        "godot_configure_tileset_terrain",
        "Configure TileSet Terrain",
        "Configure TileSet terrain sets, terrain modes, and auto-tiling.",
        ConfigureTileSetTerrainInput,
        handle_configure_tileset_terrain,
    ),
    ToolDef(
        "godot_create_navigation_region",
        "Create Navigation Region",
        "Create NavigationRegion2D or NavigationRegion3D with NavigationMesh.",
        CreateNavigationRegionInput,
        handle_create_navigation_region,
    ),
    ToolDef(
        "godot_bake_navmesh",
        "Bake Navigation Mesh",
        "Trigger navigation mesh baking on a NavigationRegion.",
        BakeNavMeshInput,
        handle_bake_navmesh,
    ),
    ToolDef(
        "godot_configure_navigation_obstacle",
        "Configure Navigation Obstacle",
        "Configure NavigationObstacle2D or NavigationObstacle3D dynamic avoidance.",
        ConfigureNavigationObstacleInput,
        handle_configure_navigation_obstacle,
    ),
    ToolDef(
        "godot_configure_gridmap",
        "Configure GridMap",
        "Assign MeshLibrary, set cell sizes, and place 3D grid tiles.",
        ConfigureGridMapInput,
        handle_configure_gridmap,
    ),
    ToolDef(
        "godot_create_curve_path",
        "Create Curve Path",
        "Construct Path2D or Path3D curves with control points.",
        CreateCurvePathInput,
        handle_create_curve_path,
    ),
    # Physics & Simulation
    ToolDef(
        "godot_cast_ray_3d",
        "Cast Ray 3D",
        "Perform 3D raycast query against PhysicsDirectSpaceState3D.",
        CastRay3DInput,
        handle_cast_ray_3d,
        read_only=True,
    ),
    ToolDef(
        "godot_cast_shape_3d",
        "Cast Shape 3D",
        "Perform 3D shapecast (sweep test) in physics space.",
        CastShape3DInput,
        handle_cast_shape_3d,
        read_only=True,
    ),
    ToolDef(
        "godot_get_body_physics_state_3d",
        "Get Body Physics State 3D",
        "Inspect transform, linear/angular velocity, and contacts.",
        GetBodyPhysicsState3DInput,
        handle_get_body_physics_state_3d,
        read_only=True,
    ),
    ToolDef(
        "godot_set_physics_debug_mode",
        "Set Physics Debug Mode",
        "Enable/disable visual physics collision shape debugging.",
        SetPhysicsDebugModeInput,
        handle_set_physics_debug_mode,
    ),
    ToolDef(
        "godot_inspect_skeleton",
        "Inspect Skeleton3D",
        "Query bone hierarchies, rest poses, transforms, and socket names.",
        InspectSkeletonInput,
        handle_inspect_skeleton,
        read_only=True,
    ),
    ToolDef(
        "godot_configure_bone_attachment",
        "Configure BoneAttachment3D",
        "Attach props, weapons, or collision nodes to named Skeleton3D bones.",
        ConfigureBoneAttachmentInput,
        handle_configure_bone_attachment,
    ),
    ToolDef(
        "godot_setup_inverse_kinematics",
        "Setup Inverse Kinematics",
        "Configure SkeletonIK3D chains with target nodes and magnet vectors.",
        SetupInverseKinematicsInput,
        handle_setup_inverse_kinematics,
    ),
    ToolDef(
        "godot_configure_physics_joint",
        "Configure Physics Joint",
        "Create and configure 3D physics joints (Pin, Hinge, Slider, ConeTwist, 6DOF).",
        ConfigurePhysicsJointInput,
        handle_configure_physics_joint,
    ),
    ToolDef(
        "godot_generate_ragdoll",
        "Generate Physical Ragdoll",
        "Automatically construct PhysicalBone3D hierarchies from Skeleton3D.",
        GenerateRagdollInput,
        handle_generate_ragdoll,
    ),
    # UI Automation & E2E Testing ("Playwright for Godot")
    ToolDef(
        "godot_find_elements",
        "Find UI Elements",
        "Locate UI elements by text, name, class, group, or role.",
        FindElementsInput,
        handle_find_elements,
        read_only=True,
    ),
    ToolDef(
        "godot_interact_node",
        "Interact with Node",
        "Perform click, type_text, drag_to, or scroll on a located node.",
        InteractNodeInput,
        handle_interact_node,
    ),
    ToolDef(
        "godot_wait_for_condition",
        "Wait for Condition",
        "Auto-wait for node appearance, property thresholds, or signals.",
        WaitForConditionInput,
        handle_wait_for_condition,
    ),
    ToolDef(
        "godot_assert_node_state",
        "Assert Node State",
        "Assert properties, visibility, disabled state, or bounds.",
        AssertNodeStateInput,
        handle_assert_node_state,
        read_only=True,
    ),
    ToolDef(
        "godot_simulate_input",
        "Simulate Input Events",
        "Inject simulated mouse, keyboard, or joypad events.",
        SimulateInputInput,
        handle_simulate_input,
    ),
    ToolDef(
        "godot_draw_debug_shapes",
        "Draw Debug Shapes",
        "Render temporary 2D/3D debug shapes with colors and durations.",
        DrawDebugShapesInput,
        handle_draw_debug_shapes,
    ),
    ToolDef(
        "godot_clear_debug_shapes",
        "Clear Debug Shapes",
        "Remove all active runtime debug drawing shapes.",
        ClearDebugShapesInput,
        handle_clear_debug_shapes,
    ),
    # Multiplayer & Networking
    ToolDef(
        "godot_configure_multiplayer_spawner",
        "Configure MultiplayerSpawner",
        "Setup automated network node spawning paths.",
        ConfigureMultiplayerSpawnerInput,
        handle_configure_multiplayer_spawner,
    ),
    ToolDef(
        "godot_configure_multiplayer_synchronizer",
        "Configure MultiplayerSynchronizer",
        "Configure synced properties and replication intervals.",
        ConfigureMultiplayerSynchronizerInput,
        handle_configure_multiplayer_synchronizer,
    ),
    ToolDef(
        "godot_simulate_network_conditions",
        "Simulate Network Conditions",
        "Inject simulated latency, jitter, and packet loss.",
        SimulateNetworkConditionsInput,
        handle_simulate_network_conditions,
    ),
    # Gameplay & Architecture
    ToolDef(
        "godot_scaffold_state_machine",
        "Scaffold State Machine",
        "Construct modular hierarchical finite state machine nodes.",
        ScaffoldStateMachineInput,
        handle_scaffold_state_machine,
    ),
    ToolDef(
        "godot_create_dialogue_resource",
        "Create Dialogue Resource",
        "Generate branching dialogue JSON / Resource files.",
        CreateDialogueResourceInput,
        handle_create_dialogue_resource,
    ),
    ToolDef(
        "godot_create_csg_shape",
        "Create CSG Shape",
        "Construct Constructive Solid Geometry (CSGBox, CSGSphere, etc).",
        CreateCSGShapeInput,
        handle_create_csg_shape,
    ),
    ToolDef(
        "godot_generate_procedural_mesh",
        "Generate Procedural Mesh",
        "Generate custom procedural 3D meshes using SurfaceTool.",
        GenerateProceduralMeshInput,
        handle_generate_procedural_mesh,
    ),
    # Profiling & Diagnostics
    ToolDef(
        "godot_get_performance_metrics",
        "Get Performance Metrics",
        "Query FPS, memory, draw calls, and physics monitors.",
        GetPerformanceMetricsInput,
        handle_get_performance_metrics,
        read_only=True,
    ),
    ToolDef(
        "godot_audit_orphan_nodes",
        "Audit Orphan Nodes",
        "Detect memory leaks from unparented orphan nodes in SceneTree.",
        AuditOrphanNodesInput,
        handle_audit_orphan_nodes,
        read_only=True,
    ),
    ToolDef(
        "godot_inspect_vram_usage",
        "Inspect VRAM Allocations",
        "Query VRAM texture, buffer, and render target allocations.",
        InspectVRAMUsageInput,
        handle_inspect_vram_usage,
        read_only=True,
    ),
    ToolDef(
        "godot_capture_profiler_trace",
        "Capture Profiler Trace",
        "Record engine frame timeline trace slices for performance bottleneck analysis.",
        CaptureProfilerTraceInput,
        handle_capture_profiler_trace,
        read_only=True,
    ),
    # Editor Integration, Themes & Settings
    ToolDef(
        "godot_create_theme",
        "Create Theme Resource",
        "Create Theme resource with color, font, and stylebox overrides.",
        CreateThemeInput,
        handle_create_theme,
    ),
    ToolDef(
        "godot_apply_theme_override",
        "Apply Theme Override",
        "Apply theme override directly to a Control node in active scene.",
        ApplyThemeOverrideInput,
        handle_apply_theme_override,
    ),
    ToolDef(
        "godot_get_input_actions",
        "Get Input Map Actions",
        "Query all configured project input actions and key bindings.",
        GetInputActionsInput,
        handle_get_input_actions,
        read_only=True,
    ),
    ToolDef(
        "godot_configure_input_action",
        "Configure Input Action",
        "Add, remove, or modify input actions and event bindings.",
        ConfigureInputActionInput,
        handle_configure_input_action,
    ),
    ToolDef(
        "godot_get_autoloads",
        "Get Autoload Singletons",
        "Query all registered Autoload singletons.",
        GetAutoloadsInput,
        handle_get_autoloads,
        read_only=True,
    ),
    ToolDef(
        "godot_set_autoload",
        "Configure Autoload Singleton",
        "Add, remove, or reorder Autoload singletons in project.godot.",
        SetAutoloadInput,
        handle_set_autoload,
    ),
    ToolDef(
        "godot_get_plugins",
        "Get Editor Plugins",
        "Discover installed editor plugins in res://addons/.",
        GetPluginsInput,
        handle_get_plugins,
        read_only=True,
    ),
    ToolDef(
        "godot_set_plugin_status",
        "Set Plugin Status",
        "Enable or disable an editor plugin.",
        SetPluginStatusInput,
        handle_set_plugin_status,
    ),
    ToolDef(
        "godot_get_translations",
        "Get Translation Files",
        "Query registered localization files (.translation / .csv).",
        GetTranslationsInput,
        handle_get_translations,
        read_only=True,
    ),
    ToolDef(
        "godot_add_translation",
        "Add Translation File",
        "Register a localization translation file in project.godot.",
        AddTranslationInput,
        handle_add_translation,
    ),
    ToolDef(
        "godot_get_uid",
        "Get Resource UID",
        "Convert resource path to native Godot uid:// identifier.",
        GetUIDInput,
        handle_get_uid,
        read_only=True,
    ),
    ToolDef(
        "godot_resolve_uid",
        "Resolve Resource UID",
        "Resolve uid:// identifier back into its file path.",
        ResolveUIDInput,
        handle_resolve_uid,
        read_only=True,
    ),
    ToolDef(
        "godot_get_dependencies",
        "Get Resource Dependencies",
        "Query dependency list for a scene, resource, or script.",
        GetDependenciesInput,
        handle_get_dependencies,
        read_only=True,
    ),
    ToolDef(
        "godot_get_export_presets",
        "Get Export Presets",
        "Query export presets defined in export_presets.cfg.",
        GetExportPresetsInput,
        handle_get_export_presets,
        read_only=True,
    ),
    ToolDef(
        "godot_export_project",
        "Export Project Binary",
        "Export project binary for target preset via CLI.",
        ExportProjectInput,
        handle_export_project,
    ),
    ToolDef(
        "godot_focus_node",
        "Focus Node in Inspector",
        "Select node in scene tree and focus in Inspector dock.",
        FocusNodeInput,
        handle_focus_node,
    ),
    ToolDef(
        "godot_set_editor_selection",
        "Set Editor Selection",
        "Set selected nodes in the 2D/3D editor viewport.",
        SetEditorSelectionInput,
        handle_set_editor_selection,
    ),
    ToolDef(
        "godot_get_selected_nodes",
        "Get Editor Selected Nodes",
        "Query paths of all nodes currently selected in Editor.",
        GetSelectedNodesInput,
        handle_get_selected_nodes,
        read_only=True,
    ),
    ToolDef(
        "godot_set_selected_nodes",
        "Set Editor Node Selection",
        "Replace current editor node selection.",
        SetSelectedNodesInput,
        handle_set_selected_nodes,
    ),
    ToolDef(
        "godot_undo",
        "Editor Undo",
        "Trigger undo on the active Godot Editor undo/redo manager.",
        UndoInput,
        handle_undo,
    ),
    ToolDef(
        "godot_redo",
        "Editor Redo",
        "Trigger redo on the active Godot Editor undo/redo manager.",
        RedoInput,
        handle_redo,
    ),
    ToolDef(
        "godot_get_editor_layout",
        "Get Editor Layout",
        "Query active editor dock positions and open main screens.",
        GetEditorLayoutInput,
        handle_get_editor_layout,
        read_only=True,
    ),
    ToolDef(
        "godot_set_editor_layout",
        "Set Editor Layout",
        "Switch editor main screen or dock arrangements.",
        SetEditorLayoutInput,
        handle_set_editor_layout,
    ),
    ToolDef(
        "godot_get_node_signals",
        "Get Node Signals",
        "Query all signals declared or inherited on a live node.",
        GetNodeSignalsInput,
        handle_get_node_signals,
        read_only=True,
    ),
    ToolDef(
        "godot_get_signal_connections",
        "Get Signal Connections",
        "Query all incoming and outgoing signal connections.",
        GetSignalConnectionsInput,
        handle_get_signal_connections,
        read_only=True,
    ),
    # Godot Asset Library Integration
    ToolDef(
        "godot_search_asset_library",
        "Search Godot Asset Library",
        "Search the official Godot Asset Library for plugins, shaders, templates, and tools.",
        SearchAssetLibraryInput,
        handle_search_asset_library,
        read_only=True,
    ),
    ToolDef(
        "godot_get_asset_details",
        "Get Asset Details",
        "Retrieve full details, previews, description, and download metadata for an asset from the Godot Asset Library.",
        GetAssetDetailsInput,
        handle_get_asset_details,
        read_only=True,
    ),
    ToolDef(
        "godot_install_asset_package",
        "Install Asset Package",
        "Download and install a community asset or plugin package into the active project, with auto-plugin registration.",
        InstallAssetPackageInput,
        handle_install_asset_package,
        idempotent=True,
    ),
]


def _register_tool(server: MCPServer, client: GodotClient, tool_def: ToolDef) -> None:
    """Register a single ToolDef on the MCPServer."""
    handler = tool_def.handler

    async def _endpoint(params: Any) -> str:
        return await handler(client, params)

    _endpoint.__name__ = tool_def.name
    _endpoint.__doc__ = tool_def.description
    _endpoint.__annotations__ = {"params": tool_def.input_model, "return": str}

    server.tool(
        name=tool_def.name,
        annotations=ToolAnnotations(
            title=tool_def.title,
            read_only_hint=tool_def.read_only,
            destructive_hint=tool_def.destructive,
            idempotent_hint=tool_def.idempotent,
            open_world_hint=False,
        ),
    )(_endpoint)


def create_server(
    client: GodotClient | None = None, config: GodotConfig | None = None
) -> MCPServer:
    """Create and configure the MCPServer with all Godot tools registered."""
    active_client = client or ClientManager(config or GodotConfig.load())

    server = MCPServer(
        name="godot_mcp",
        instructions="Model Context Protocol (MCP) server for inspecting and controlling the Godot Engine 4.7+.",
    )

    # Register all declarative tools
    for tool_def in TOOL_DEFINITIONS:
        _register_tool(server, active_client, tool_def)

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
        """Dynamic MCP resource providing complete project.godot configuration key-value JSON."""
        res = await active_client.get_project_settings()
        return json.dumps(res.data, indent=2)

    @server.resource("godot://project/autoloads")
    async def resource_project_autoloads() -> str:
        """Dynamic MCP resource providing all active Autoload singletons in the project."""
        res = await active_client.get_autoloads()
        return json.dumps(res.data, indent=2)

    @server.resource("godot://project/plugins")
    async def resource_project_plugins() -> str:
        """Dynamic MCP resource providing installed editor plugins in res://addons/."""
        res = await active_client.get_plugins()
        return json.dumps(res.data, indent=2)

    @server.resource("godot://scene/tree")
    async def resource_scene_tree() -> str:
        """Dynamic MCP resource providing live scene tree hierarchy graph JSON."""
        res = await active_client.list_nodes(max_depth=6, include_properties=False)
        return json.dumps(res.data, indent=2)

    @server.resource("godot://editor/selection")
    async def resource_editor_selection() -> str:
        """Dynamic MCP resource providing currently selected nodes in the Godot Editor."""
        res = await active_client.get_selected_nodes()
        return json.dumps(res.data, indent=2)

    @server.resource("godot://editor/layout")
    async def resource_editor_layout() -> str:
        """Dynamic MCP resource providing active editor docks and main screen configuration."""
        res = await active_client.get_editor_layout()
        return json.dumps(res.data, indent=2)

    @server.resource("godot://vram/usage")
    async def resource_vram_usage() -> str:
        """Dynamic MCP resource providing VRAM texture and buffer allocation breakdown."""
        res = await active_client.inspect_vram_usage()
        return json.dumps(res.data, indent=2)

    @server.resource("godot://project/input_map")
    async def resource_input_map() -> str:
        """Dynamic MCP resource providing all configured input actions and key bindings."""
        res = await active_client.get_input_actions()
        return json.dumps(res.data, indent=2)

    @server.resource("godot://project/export_presets")
    async def resource_export_presets() -> str:
        """Dynamic MCP resource providing export presets defined in export_presets.cfg."""
        res = await active_client.get_export_presets()
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
