# Godot Engine MCP (`godot-engine-mcp`)

A modern Model Context Protocol (MCP) server and Live Editor Bridge for the **Godot Engine 4.7+**.

Built with the official **Python MCP SDK v2.0+** (`mcp>=2.0.0`, FastMCP, 2026-07-28 stateless protocol), strict Pydantic v2 schemas, type safety via Astral `ty`, and a robust **dual-tier hybrid bridge** architecture.

---

## Architecture Overview

Godot Engine MCP operates across three complementary layers:

1. **Live Editor Bridge (`addons/godot_mcp/`)**:
   A modular GDScript `EditorPlugin` running inside Godot that hosts a local WebSocket IPC server (`ws://127.0.0.1:3118/ws`). It provides live access to:
   - `EditorInterface` and active scene tree hierarchy
   - Interactive node creation and modification with full `EditorUndoRedoManager` support
   - Signal wiring, script attachment, and hot reloading
   - 3D Physics geometric queries (`intersect_ray`, `intersect_shape`, `cast_motion`)
   - High-fidelity 2D/3D viewport screenshot capture for multimodal AI models

2. **Headless CLI Fallback (`godot --headless`)**:
   When the Godot Editor is not open, the server seamlessly executes offline operations via the Godot binary:
   - GDScript syntax validation and compilation diagnostics (`godot --check-only`)
   - `project.godot` settings reading and modification
   - Project file and resource discovery (`res://` asset queries)
   - Subprocess project execution and headless test suite running (including GUT unit tests)

3. **Semantic GDScript Language Server (LSP)**:
   Connects directly to Godot's built-in Language Server (`tcp://127.0.0.1:6005`) with offline AST fallback for symbol definition queries, references, hover documentation, and cross-file semantic renames.

```text
┌────────────────────────────────────────────────────────┐
│                      AI Client                         │
│         (Cursor / Claude / Gemini / Antigravity)       │
└───────────────────────────┬────────────────────────────┘
                            │ MCP (stdio / SSE)
┌───────────────────────────▼────────────────────────────┐
│              Python MCP Server (godot_mcp)             │
│   FastMCP 4 / MCP SDK v2 + Pydantic v2 + ty + ruff     │
└─────────────┬────────────────────────────┬─────────────┘
              │ Live IPC (WebSocket)       │ Headless CLI (`godot --headless`)
┌─────────────▼─────────────┐ ┌────────────▼─────────────┐
│ Godot Editor (Active)     │ │ Godot CLI Runner         │
│ - addons/godot_mcp plugin │ │ - Offline script checks  │
│ - Live SceneTree & Editor │ │ - Headless test runner   │
│ - Undo/Redo & Viewports   │ │ - project.godot edits    │
└───────────────────────────┘ └──────────────────────────┘
```text

---

## Tool Catalog

All tools adhere to MCP best practices, providing clear docstrings, Pydantic v2 validation, dual formatting (`markdown` and `json`), and explicit tool annotations (`read_only_hint`, `destructive_hint`, `idempotent_hint`, `open_world_hint`).

### Project & Version Management

- `godot_get_version`: Probes engine version, build type, active project, and connection mode.
- `godot_get_project_settings`: Queries configuration settings from `project.godot`.
- `godot_set_project_setting`: Writes or updates configuration values in `project.godot`.
- `godot_list_project_files`: Searches project assets, scenes (`.tscn`), scripts (`.gd`), and textures.
- `godot_get_autoloads`: Queries all registered Autoload singletons in `project.godot`.
- `godot_set_autoload`: Adds, removes, or reorders Autoload singletons.
- `godot_get_plugins`: Discovers installed editor plugins in `res://addons/`.
- `godot_set_plugin_status`: Dynamically enables or disables editor addons.
- `godot_get_uid`: Converts a resource path into a persistent Godot 4 `uid://...` identifier.
- `godot_resolve_uid`: Resolves `uid://...` identifiers back into filesystem resource paths.
- `godot_get_dependencies`: Queries the dependency list for a scene, resource, or script.
- `godot_get_translations`: Queries registered localization files (`.translation` / `.csv`).
- `godot_add_translation`: Registers localization translation tables into `project.godot`.
- `godot_get_export_presets`: Queries export targets configured in `export_presets.cfg`.
- `godot_export_project`: Triggers automated headless project builds via Godot CLI.

### Official Godot Asset Library Integration

- `godot_search_asset_library`: Searches the official Godot Asset Library for plugins, shaders, templates, and tools.
- `godot_get_asset_details`: Retrieves full metadata, descriptions, previews, and download links for an asset ID.
- `godot_install_asset_package`: Downloads and extracts community ZIP packages into `res://addons/` with automated plugin activation in `project.godot`.

### Scene Graph, Nodes & Hierarchy Mutation

- `godot_list_nodes`: Traverses the active scene tree with configurable depth and property filtering.
- `godot_get_node`: Inspects node properties, attached scripts, transforms, groups, and signals.
- `godot_create_node`: Adds a node of any Godot class with initial properties and script binding.
- `godot_modify_node`: Updates properties on existing nodes with Undo/Redo history.
- `godot_delete_node`: Safely removes a node from the active scene tree.
- `godot_reparent_node`: Moves a node to a new parent in the active scene tree.
- `godot_duplicate_node`: Deep duplicates a node with signal and script flags.
- `godot_set_node_owner`: Sets or synchronizes the owner property of a node.
- `godot_connect_signal`: Connects signals between nodes and target handler methods.
- `godot_get_node_signals`: Inspects all signals declared or inherited on a node.
- `godot_get_signal_connections`: Queries all incoming and outgoing signal connections for a node.
- `godot_instantiate_scene`: Instantiates `.tscn` packed scene files into the active scene.
- `godot_save_scene`: Saves the active scene or exports to a target `.tscn` file.
- `godot_open_scene`: Opens a scene file in the Godot Editor workspace.
- `godot_create_scene`: Creates a new scene file with root node and saves to disk.
- `godot_diff_scene`: Compares two scene files (`.tscn`) and generates structural diffs.

### Scripting, Reflection & Semantic LSP

- `godot_validate_script`: Checks GDScript code or files for syntax errors and compilation diagnostics.
- `godot_create_script`: Generates GDScript files with template code and class inheritance.
- `godot_attach_script`: Attaches or detaches a GDScript to/from an active node.
- `godot_reload_scripts`: Force-reloads modified GDScript resources in engine memory.
- `godot_get_node_script_info`: Inspects exported properties, methods, constants, and signals on a node.
- `godot_get_class_info`: Queries class inheritance, properties, methods, and signals from `ClassDB`.
- `godot_get_documentation`: Fetches built-in documentation for classes, methods, and properties.
- `godot_evaluate_expression`: Safely evaluates GDScript expressions at runtime.
- `godot_lsp_query`: Queries symbol definitions, references, or hover docs via GDScript LSP.
- `godot_lsp_rename`: Performs cross-file semantic symbol renaming.

### 3D Physics, Collisions, Skeletons & Constraints

- `godot_cast_ray_3d`: Performs 3D raycast queries against `PhysicsDirectSpaceState3D`.
- `godot_cast_shape_3d`: Performs 3D shapecasts (sweep tests) in physics space.
- `godot_get_body_physics_state_3d`: Inspects transform, linear/angular velocity, and contact telemetry.
- `godot_set_physics_debug_mode`: Enables or disables visual physics collision shape wireframes.
- `godot_create_collision_polygon`: Generates 2D/3D collision polygons from vertices or alpha masks.
- `godot_inspect_skeleton`: Queries bone hierarchies, rest poses, transforms, and socket names on `Skeleton3D`.
- `godot_configure_bone_attachment`: Attaches props or collision nodes to named bones.
- `godot_setup_inverse_kinematics`: Configures `SkeletonIK3D` chains with target nodes and magnet vectors.
- `godot_configure_physics_joint`: Configures 3D physics joints (Pin, Hinge, Slider, ConeTwist, 6DOF).
- `godot_generate_ragdoll`: Automatically constructs `PhysicalBone3D` hierarchies from `Skeleton3D`.

### Materials, VFX & Spatial Rendering

- `godot_validate_shader`: Compiles and checks Godot Shader Language code for errors.
- `godot_create_material`: Instantiates `StandardMaterial3D`, `ORMMaterial3D`, or `ShaderMaterial`.
- `godot_create_shader`: Generates custom shaders (`.gdshader`) with starter boilerplate.
- `godot_set_shader_param`: Sets uniform parameter values on a `ShaderMaterial`.
- `godot_configure_particles`: Tunes `GPUParticles2D/3D` and `CPUParticles` emission parameters.
- `godot_configure_environment`: Adjusts `WorldEnvironment` background, glow, tonemap, and ambient light.
- `godot_configure_camera`: Creates and tunes `Camera2D` or `Camera3D` viewports and FOV.
- `godot_configure_render_settings`: Configures anti-aliasing, shadow quality, V-Sync, and upscaling.
- `godot_capture_viewport`: Captures high-resolution viewport frames for AI vision inspection.
- `godot_configure_lightmap_gi`: Configures 3D GI pipelines (`LightmapGI`, `VoxelGI`, `ReflectionProbe`).
- `godot_bake_lightmaps`: Triggers lightmap or voxel GI baking for the active scene.
- `godot_setup_xr_rig`: Scaffolds `XROrigin3D`, `XRCamera3D`, and `XRController3D` tracking rigs.
- `godot_configure_xr_passthrough`: Configures OpenXR passthrough modes and foveated rendering.
- `godot_dispatch_compute_shader`: Dispatches compute shaders on GPU via `RenderingDevice`.
- `godot_inspect_rendering_device`: Queries GPU `RenderingDevice` limits, vendor, and device capabilities.
- `godot_scatter_multimesh`: High-performance GPU-instanced scattering across a 3D bounding area.
- `godot_configure_lod_manager`: Configures visibility ranges, distance thresholds, and cross-fade modes.

### World Building, TileMaps, GridMaps & Navigation

- `godot_create_tilemap_layer`: Adds a `TileMapLayer` node with `TileSet` binding.
- `godot_set_tilemap_cells`: Places or clears tiles on a `TileMapLayer` coordinate grid.
- `godot_get_tilemap_cells`: Reads placed cell coordinates and atlas coordinates from `TileMapLayer`.
- `godot_configure_tileset_terrain`: Configures `TileSet` terrain sets, terrain modes, and autotiling peering bits.
- `godot_create_navigation_region`: Creates `NavigationRegion2D` or `NavigationRegion3D` with `NavigationMesh`.
- `godot_bake_navmesh`: Triggers navigation mesh baking on a `NavigationRegion`.
- `godot_configure_navigation_obstacle`: Configures `NavigationObstacle2D/3D` dynamic avoidance.
- `godot_configure_gridmap`: Assigns `MeshLibrary`, cell sizes, and places 3D grid tiles.
- `godot_create_curve_path`: Constructs `Path2D` or `Path3D` curves with control points.

### UI Automation & E2E Testing ("Playwright for Godot")

- `godot_find_elements`: Locates UI elements by text, name, class, group, or accessibility role.
- `godot_interact_node`: Performs `click`, `type_text`, `drag_to`, or `scroll` on a located node.
- `godot_wait_for_condition`: Auto-waits for node appearance, property thresholds, or signal emissions.
- `godot_assert_node_state`: Asserts properties, visibility, disabled state, or bounding rectangles.
- `godot_simulate_input`: Injects simulated mouse, keyboard, or joypad input events.
- `godot_draw_debug_shapes`: Renders temporary 2D/3D debug shapes with colors and durations.
- `godot_clear_debug_shapes`: Removes all active runtime debug drawing shapes.

### Audio, Diagnostics & Profiling

- `godot_configure_audio_bus`: Adds, renames, mutes, solos, or routes `AudioServer` buses.
- `godot_set_bus_effect`: Adds or adjusts real-time audio effects on an audio bus.
- `godot_get_audio_layout`: Queries complete `AudioServer` bus hierarchy and effect chains.
- `godot_get_performance_metrics`: Queries real-time FPS, memory, draw calls, and physics monitors.
- `godot_audit_orphan_nodes`: Detects memory leaks from unparented orphan nodes in `SceneTree`.
- `godot_inspect_vram_usage`: Queries VRAM texture, buffer, and render target allocations.
- `godot_capture_profiler_trace`: Records engine frame timeline trace slices for bottleneck analysis.
- `godot_audit_assets`: Scans project for unused assets, missing dependencies, or broken paths.
- `godot_clean_orphans`: Removes or quarantines unreferenced and orphaned asset files.
- `godot_get_texture_info`: Queries dimensions, format, VRAM compression, and mipmaps.

### Gameplay Scaffolding & Testing

- `godot_scaffold_state_machine`: Constructs modular hierarchical finite state machine nodes.
- `godot_create_dialogue_resource`: Generates branching dialogue JSON / Resource files.
- `godot_create_csg_shape`: Constructs Constructive Solid Geometry (`CSGBox`, `CSGSphere`, etc.).
- `godot_generate_procedural_mesh`: Generates custom procedural 3D meshes using `SurfaceTool`.
- `godot_configure_multiplayer_spawner`: Configures automated network node spawning paths.
- `godot_configure_multiplayer_synchronizer`: Configures synced properties and replication intervals.
- `godot_simulate_network_conditions`: Injects simulated latency, jitter, and packet loss.
- `godot_generate_gut_test`: Scaffolds GUT test scripts for target classes or scripts.
- `godot_run_gut_tests`: Executes GUT test suites headlessly and parses test outcomes.

---

## Dynamic MCP Resources (`godot://`)

Godot MCP provides dynamic, self-updating URI resources for live AI context:

| Resource URI | Description |
| --- | --- |
| `godot://project/settings` | Complete `project.godot` configuration key-value dictionary JSON. |
| `godot://scene/active/tree` | Live scene tree hierarchy of the active editor scene. |
| `godot://performance/metrics` | Real-time performance telemetry (FPS, process times, VRAM, draw calls). |
| `godot://audio/layout` | `AudioServer` bus hierarchy and active audio effect chains. |
| `godot://editor/selection` | Paths of all nodes currently selected in the Godot Editor. |
| `godot://editor/layout` | Active editor docks and main screen workspace configuration. |
| `godot://vram/usage` | VRAM texture, buffer, and render target allocation breakdown. |
| `godot://project/autoloads` | All registered Autoload singletons in the project. |
| `godot://project/plugins` | Installed editor plugins in `res://addons/`. |
| `godot://project/input_map` | All configured project input actions and key bindings. |
| `godot://project/export_presets` | Export presets defined in `export_presets.cfg`. |
| `godot://logs/editor.log` | Recent Godot engine and editor log output. |
| `godot://engine/classes/{class_name}` | Dynamic template for `ClassDB` property, method, signal, and enum reflection. |

---

## Workflow Prompts (`prompt://`)

Pre-engineered guided workflows for common game development tasks:

- `prompt://fix_scene_warnings`: Inspects active nodes and guides automated resolution of configuration warnings.
- `prompt://create_rich_ui`: Guided workflow for constructing responsive, themed Godot 4 GUI layouts.
- `prompt://scaffold_character`: Guided workflow for setting up complete 2D/3D character controllers with movement scripts.

---

## Quick Start

### 1. Requirements

- Python 3.14+ managed with [uv](https://docs.astral.sh/uv/)
- Godot Engine 4.7+ (or 4.7.1+)

### 2. Setup a Godot Project

You can install the `godot_mcp` editor addon directly using `uvx` without needing to clone the repository:

```bash
# Install and auto-enable the addon in your Godot project:
uvx --from git+https://github.com/mcintalmo/godot-engine-mcp godot-engine-mcp install-addon /path/to/your/godot/project

# Check connection status:
uvx --from git+https://github.com/mcintalmo/godot-engine-mcp godot-engine-mcp probe
```text

Or if developing locally from source:

```bash
# Clone repository
git clone https://github.com/mcintalmo/godot-engine-mcp.git
cd godot-engine-mcp

# Sync dependencies with uv
uv sync

# Install addon to project
uv run godot-engine-mcp install-addon /path/to/your/godot/project
```text

---

## Client Configuration

### Claude Desktop

Add to `claude_desktop_config.json`:

#### Option A: Direct via GitHub (Recommended)

```json
{
  "mcpServers": {
    "godot-engine": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/mcintalmo/godot-engine-mcp",
        "godot-engine-mcp"
      ],
      "env": {
        "GODOT_PATH": "/Applications/Godot.app/Contents/MacOS/Godot",
        "GODOT_PROJECT_PATH": "/path/to/your/godot/project"
      }
    }
  }
}
```text

#### Option B: From Local Clone

```json
{
  "mcpServers": {
    "godot-engine": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/godot-engine-mcp",
        "run",
        "godot-engine-mcp"
      ],
      "env": {
        "GODOT_PATH": "/Applications/Godot.app/Contents/MacOS/Godot",
        "GODOT_PROJECT_PATH": "/path/to/your/godot/project"
      }
    }
  }
}
```text

### Cursor / Windsurf

Add to `.cursor/mcp.json` or `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "godot-engine": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/mcintalmo/godot-engine-mcp",
        "godot-engine-mcp"
      ],
      "env": {
        "GODOT_PATH": "/Applications/Godot.app/Contents/MacOS/Godot",
        "GODOT_PROJECT_PATH": "/path/to/your/godot/project"
      }
    }
  }
}
```text

### Gemini Antigravity IDE

Add to `.gemini/antigravity-ide/mcp_config.json`:

```json
{
  "mcpServers": {
    "godot-engine": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/mcintalmo/godot-engine-mcp",
        "godot-engine-mcp"
      ],
      "env": {
        "GODOT_PATH": "/Applications/Godot.app/Contents/MacOS/Godot",
        "GODOT_PROJECT_PATH": "/path/to/your/godot/project"
      }
    }
  }
}
```text

---

## Development & Verification

```bash
# Run unit & integration test suite
uv run pytest

# Check strict static typing
uv run ty check

# Check linting and formatting
uv run ruff check
uv run ruff format --check
```text

---

## License

MIT License. See [LICENSE](LICENSE) for details.
