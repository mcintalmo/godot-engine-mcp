# Godot MCP Roadmap

This roadmap documents the architectural gap analysis and planned feature evolution for `godot-mcp` relative to peer Game Engine and DCC MCP implementations (Unity MCP, Unreal Engine MCP, Blender MCP).

---

## 🎯 Capability Comparison & Target State

| Feature Area | Status | Target Capabilities |
|---|---|---|
| **Scene & Node Operations** | ✅ Completed | Node creation/modification/deletion, full property deserialization (`Vector2/3`, `Color`, `Resources`), Undo/Redo support, standalone scene creation (`godot_create_scene`), scene switching (`godot_open_scene`), real-time warning diagnostics. |
| **Engine Reflection & ClassDB** | ✅ Completed | `godot_get_class_info`, `godot_get_documentation`, `godot_get_enum_constants`, eliminating LLM hallucinations across Godot 3 vs Godot 4 API changes. |
| **Shader & Material Authoring** | ✅ Completed | `godot_validate_shader` (`.gdshader` compilation diagnostics), `godot_create_material` (`StandardMaterial3D`, `ShaderMaterial`, PBR properties). |
| **MCP Dynamic Resources & Prompts** | ✅ Completed | Dynamic `godot://` URI resources (`godot://project/settings`, `godot://scene/active/tree`, `godot://engine/classes/{ClassName}`, `godot://logs/editor.log`, `godot://performance/metrics`) and workflow prompts (`prompt://fix-scene-warnings`, `prompt://create-rich-ui`, `prompt://scaffold-character`). |
| **Asset & Reimport Pipeline** | ✅ Completed | `godot_reimport_asset` (`.import` configuration, texture compression presets, pixel art settings), `godot_create_collision_polygon`. |
| **Animation, Keyframes & Timeline** | ✅ Completed | `godot_create_animation` (programmatic property tracks, transform tracks, method call tracks, easing curves, keyframes). |
| **Level Design & Geometry** | ✅ Completed | `godot_set_tilemap_cells` / `godot_get_tilemap_cells` (batch paint/erase cells on `TileMapLayer`), `godot_create_tilemap_layer`, `godot_bake_navmesh`, `godot_create_navigation_region`. |
| **GDScript Semantic LSP Integration** | ✅ Completed | Connect directly to Godot's built-in LSP server (`port 6005`) for cross-file symbol definitions, references, hover documentation, and semantic renaming refactors. |
| **Runtime Profiler & Telemetry** | ✅ Completed | `godot_get_performance_metrics` (`Performance.get_monitor()`: FPS, Draw Calls, VRAM, Objects, Memory Leaks) and dynamic `godot://performance/metrics` resource. |


---

## 📅 Phased Release Plan

### Phase 1: Core Engine Intelligence & Protocol Expansion
- [x] Standalone scene creation & scene tab switching (`godot_create_scene`, `godot_open_scene`).
- [x] **Engine Reflection (`godot_get_class_info`)**: Inspect class inheritance, properties, methods, signals, and constants via `ClassDB`.
- [x] **Engine Documentation (`godot_get_documentation`)**: Fetch official Godot docstrings, property summaries, and tutorials directly from the engine runtime.
- [x] **Shader Validation (`godot_validate_shader`)**: Real-time syntax and compilation checking for `.gdshader` files.
- [x] **MCP Dynamic Resources**: Expose `godot://` resources for project settings, active scene tree, ClassDB metadata, and logs.
- [x] **MCP Workflow Prompts**: Provide standard prompts for automated scene warning resolution, character scaffolding, and responsive UI building.

### Phase 2: Material, Asset & Shape Pipelines
- [x] **PBR Material Builder (`godot_create_material`)**: Rapid instantiation and configuration of `StandardMaterial3D`, `ShaderMaterial`, `CanvasItemMaterial`, `ORMMaterial3D`.
- [x] **Asset Reimport Automation (`godot_reimport_asset`)**: Reimport triggers and import preset automation (e.g. 2D Nearest Neighbor for Pixel Art, High Quality 3D, Uncompressed Audio).
- [x] **Collision Polygon Generator (`godot_create_collision_polygon`)**: Generate 2D/3D polygon colliders (`CollisionPolygon2D` / `CollisionPolygon3D`) from vertex arrays.



### Phase 3: Animation, Level Design & Semantic LSP
- [x] **Animation Track & Keyframe Authoring (`godot_create_animation`)**: Add tracks (property, 3D transform, method call), insert keyframes, set transition easing curves, and save `.tres` / attach to `AnimationPlayer`.
- [x] **TileMapLayer Cell Painting (`godot_set_tilemap_cells`, `godot_get_tilemap_cells`, `godot_create_tilemap_layer`)**: Programmatically create, paint, erase, and query tile maps on Godot 4.7+ `TileMapLayer` and legacy `TileMap` nodes.
- [x] **NavMesh Baking (`godot_bake_navmesh`, `godot_create_navigation_region`)**: Trigger asynchronous navigation mesh baking and configure agent profiles on `NavigationRegion3D` / `NavigationRegion2D`.
- [x] **Godot LSP Client (`godot_lsp_query`, `godot_lsp_rename`)**: Query GDScript symbols, definitions, find references, inspect docstrings/signatures, and perform safe cross-file renaming on Godot LSP port 6005 with offline static fallback.
- [x] **Performance Monitor Telemetry (`godot_get_performance_metrics`, `godot://performance/metrics`)**: Real-time telemetry stream and dynamic MCP resource for framerate (FPS), draw calls, frame process times, VRAM, and orphan node leak tracking.

### Phase 4: UI Design, Audio & Interactive Debugging
- [x] **Theme & UI Styling Engine (`godot_create_theme`, `godot_apply_theme_override`)**: Create and save Godot 4 Theme resources (`.tres`) with custom `StyleBoxFlat` rounded corners, borders, shadows, colors, constants, and fonts; apply live node overrides with `UndoRedo`.
- [x] **Audio Bus & Effect Pipeline (`godot_get_audio_layout`, `godot_configure_audio_bus`, `godot_set_bus_effect`, `godot://audio/layout`)**: Programmatically query and configure `AudioServer` layout, routing, bus volumes (dB / linear), and audio effects (Reverb, EQ, Chorus, Delay, Filters, Compressors) with `.tres` persistence.
- [x] **Interactive Play Mode & Debug Control (`godot_play_scene`, `godot_stop_scene`, `godot_get_play_state`, `godot_set_play_state`)**: Interactive viewport scene playback (main, active, custom .tscn), simulation speed control (`Engine.time_scale`), pause toggle, and frame-stepping.

### Phase 5: 3D Physics & World Diagnostics
- [x] **3D Physics Debugging & Geometric Queries (`godot_cast_ray_3d`, `godot_cast_shape_3d`, `godot_get_body_physics_state_3d`, `godot_set_physics_debug_mode`)**: Raycasting (`intersect_ray`), volumetric shape sweeps (sphere/box/capsule/cylinder `intersect_shape`/`cast_motion`), live body telemetry (velocity, mass, sleeping, contacts, impulses), and collision wireframe debug overlays.

### Phase 6: Input System, WorldEnvironment & Viewport Focus
- [x] **Input Map & Actions Engine (`godot_get_input_actions`, `godot_configure_input_action`)**: Query, create, and bind input events (Keys, Mouse buttons, Gamepad buttons/axes) with deadzone configuration and permanent `project.godot` `ProjectSettings` persistence.
- [x] **WorldEnvironment & Post-Processing (`godot_configure_environment`)**: Parametric control over procedural/physical skies, ACES tonemapping, HDR glow/bloom, SSAO, SSIL, SSR, and volumetric fog with `.tres` saving or live `WorldEnvironment` node updating.
- [x] **Editor Selection & Viewport Navigation (`godot_set_editor_selection`, `godot_focus_node`)**: Programmatically select nodes in the Scene Tree dock and focus target nodes in the Inspector and 2D/3D editor workspaces.

### Phase 7: DCC / Blender 3D Import Pipeline, VFX & Build Engine
- [x] **DCC / Blender Model Instancing & GLTF Import (`godot_instantiate_model`, `godot_configure_gltf_import`)**: Programmatically instantiate `.glb`, `.gltf`, and `.blend` assets with transform placement, automated collision shape generation (`Trimesh`, `Convex`, `Box`), inherited `.tscn` packing, and `.import` LOD/shadow mesh configuration.
- [x] **VFX Particle Systems Engine (`godot_configure_particles`)**: Create and tweak `GPUParticles3D/2D` and `CPUParticles` systems with volumetric emission shapes (Sphere, Box, Ring), bursts, color gradient ramps (`GradientTexture1D`), velocities, and `ParticleProcessMaterial` `.tres` exporting.
- [x] **Project Export & Build Automation (`godot_get_export_presets`, `godot_export_project`)**: Inspect `export_presets.cfg` across all platforms (Windows, Linux, macOS, Web, Mobile) and trigger headless automated project builds via Godot CLI.

### Phase 8: Project Architecture & Event Wiring
- [x] **Autoload & Singleton Management (`godot_get_autoloads`, `godot_set_autoload`)**: Query, add, update, remove, and toggle global singletons in `project.godot` with immediate editor lifecycle registration and global script scope resolution.
- [x] **Signal Introspection & Event Wiring (`godot_get_node_signals`, `godot_connect_signal`, `godot_get_signal_connections`)**: Introspect signals on active nodes with argument definitions, bind/unbind method callables with `CONNECT_PERSIST` scene serialization, and inspect incoming/outgoing connection graphs.
- [x] **Dynamic GDScript Expression Evaluator (`godot_evaluate_expression`)**: Safely parse and execute runtime GDScript math, logical expressions, and method calls against target nodes or global scope.

### Phase 9: Shaders, Animation Trees & Localization
- [x] **Custom Shader Engineering & Uniforms (`godot_create_shader`, `godot_set_shader_param`)**: Create `.gdshader` files across shader types (Spatial, CanvasItem, Particles, Fog) with starter boilerplate and live-tweak uniform parameters on `ShaderMaterial` instances.
- [x] **AnimationTree & State Machine Graphs (`godot_configure_animation_tree`)**: Build `AnimationTree` nodes, `AnimationNodeStateMachine` roots, animation states (`AnimationNodeAnimation`), and conditional transitions with advance conditions / advance expressions.
- [x] **Localization & Translation Tables (`godot_get_translations`, `godot_add_translation`)**: Query configured translation files (`.csv`, `.po`, `.translation`), discover loaded locales, and register new localization tables into `project.godot`.

### Phase 10: Resource UIDs, Asset Dependencies & Plugin Management
- [x] **Resource UID Engine (`godot_get_uid`, `godot_resolve_uid`)**: Convert resource paths to persistent Godot 4 `uid://...` identifier strings and resolve `uid://` identifiers back to project filesystem paths.
- [x] **Asset Dependency Graph (`godot_get_dependencies`)**: Query the complete dependency list for any scene (`.tscn`), resource (`.tres`), script (`.gd`), or mesh (`.glb`) via `ResourceLoader.get_dependencies()`.
- [x] **Plugin & Addon Lifecycle Manager (`godot_get_plugins`, `godot_set_plugin_status`)**: Discover all installed editor addons in `res://addons/*/plugin.cfg`, inspect metadata, and dynamically enable/disable plugins via `EditorInterface`.

### Phase 11: Navigation Obstacles, TileSet Terrains & Scene Tree Diffing
- [x] **2D/3D Navigation Obstacles & Dynamic Avoidance (`godot_configure_navigation_obstacle`)**: Create and configure `NavigationObstacle2D` / `NavigationObstacle3D` nodes with dynamic velocity/radius RVO bubbles, static polygon boundary vertices, avoidance layers, and navmesh carving parameters.
- [x] **TileSet Terrain & Autotiling Engine (`godot_configure_tileset_terrain`)**: Create and configure `TileSet` terrain sets (`Match Corners`, `Match Sides`, `Match Corners and Sides`), named terrains with debug colors, and autotiling peering bit mappings.
- [x] **Scene Tree Diff & Audit Helper (`godot_diff_scene`)**: Perform structural hierarchy and property diffs between live edited scenes and disk files, or between two standalone `.tscn` scene files.

### Phase 12: Editor Undo/Redo & Multi-Node Selection Management
- [x] **Editor Action Undo/Redo (`godot_undo`, `godot_redo`)**: Revert or re-apply editor actions on the active scene or global history via `EditorUndoRedoManager` / `UndoRedo`.
- [x] **Multi-Node SceneTree Selection & Inspector Inspection (`godot_get_selected_nodes`, `godot_set_selected_nodes`)**: Query and programmatically manipulate active node selections in the Godot Editor SceneTree and Inspector dock via `EditorInterface.get_selection()`.

### Phase 13: Project Asset Audit, Orphan Cleanup & Texture Validation
- [x] **Project-Wide Asset Audit (`godot_audit_assets`)**: Scan the entire project for unreferenced orphan files, broken dependencies (missing files or invalid UIDs), and dependency tree reachability.
- [x] **Safe Orphan Asset Cleanup (`godot_clean_orphans`)**: Clean or quarantine unreferenced orphan files (`.tres`, `.tscn`, `.png`, `.wav`, etc.) with dry-run verification and destination folder support.
- [x] **Texture Diagnostics & VRAM Estimation (`godot_get_texture_info`)**: Inspect 2D/3D texture dimensions, pixel format, mipmaps, compression mode, and estimated VRAM footprint.

### Phase 14: Automated Engine Test Runner & GUT Integration
- [x] **Headless Engine & GUT Test Runner (`godot_run_gut_tests`)**: Execute Godot Unit Test (GUT) suites or custom test runners headlessly with automated log parsing (passed, failed, pending, assertion counts, durations, and failure stack traces).
- [x] **GUT Test Suite Scaffolding (`godot_generate_gut_test`)**: Scaffold complete GUT test scripts inheriting `GutTest` for target GDScript scripts or scenes, generating setup/teardown methods and test assertion stubs.

### Phase 15: Editor Layouts, Multi-Window Dock State & Workspace Inspector
- [x] **Editor Workspace Layout & Screen Query (`godot_get_editor_layout`)**: Query active main screen (`2D`, `3D`, `Script`, `AssetLib`), distraction-free mode state, editor UI scale, open scene tabs, and edited scene root.
- [x] **Programmatic Workspace Layout Configuration (`godot_set_editor_layout`)**: Switch main screen editor tabs, toggle distraction-free mode, and activate scene tabs.

### Phase 16: Scene Hierarchy Mutation & Node Ownership
- [x] **Node Reparenting (`godot_reparent_node`)**: Reparent nodes with `keep_global_transform` spatial preservation, owner synchronization, and child index placement (`move_child`).
- [x] **Deep Node Duplication (`godot_duplicate_node`)**: Deep clone nodes with custom flags for signal connections, group memberships, and attached script state.
- [x] **Scene Node Ownership Management (`godot_set_node_owner`)**: Programmatically assign node ownership across hierarchy subtrees to ensure proper serialization upon `.tscn` save.

### Phase 17: Live Script Lifecycle, Hot-Reload & Exported Property Reflection
- [x] **Live Script Attachment & Detachment (`godot_attach_script`)**: Attach or detach `.gd` / `.cs` script files to/from live nodes and assign initial exported property values.
- [x] **In-Memory Script Hot-Reloading (`godot_reload_scripts`)**: Force reload of GDScript resources in memory cache without restarting the editor.
- [x] **Script Introspection & Exported Properties (`godot_get_node_script_info`)**: Inspect attached script methods, signals, declared constants, and all `@export` properties with their default vs current values.

### Phase 18: Camera Presets, High-Res Viewport Capture & Rendering Pipeline
- [x] **2D & 3D Camera Configuration (`godot_configure_camera`)**: Configure Camera2D and Camera3D properties (perspective/ortho/frustum, FOV, clipping, 2D zoom, position smoothing, limits).
- [x] **Project Rendering Quality Engine (`godot_configure_render_settings`)**: Parametric control over MSAA 2D/3D, FXAA, TAA, FSR 1.0/2.2 upscaling, shadow map resolutions, and V-Sync.
- [x] **High-Res Viewport Frame Capture (`godot_capture_viewport`)**: Capture viewport frames with custom resolution downscaling, format selection (PNG/WebP/JPEG), file persistence, and base64 payload delivery for AI vision.

### Phase 19: Interactive Runtime Input Simulation & Debug Drawing
- [x] **Interactive Input Injection (`godot_simulate_input`)**: Synthesize and dispatch raw input events (`InputEventAction`, `InputEventKey`, `InputEventMouseButton`, `InputEventMouseMotion`) to the engine input pipeline.
- [x] **Viewport Debug Shape Renderer (`godot_draw_debug_shapes`)**: Render temporary 2D and 3D shapes (lines, rays, boxes, spheres, circles, rects, text) with expiration timers and color tinting.
- [x] **Debug Overlay Management (`godot_clear_debug_shapes`)**: Programmatically purge active debug shapes and overlays.

### Phase 20: "Playwright for Godot" Autonomous E2E Testing & UI Automation Engine
- [x] **Scene Element Discovery Engine (`godot_find_elements`)**: Query UI and scene hierarchy via text, role, class, node name, group, or property match with screen coordinate resolution.
- [x] **High-Level UI Interaction Primitives (`godot_interact_node`)**: Automated click, double-click, text typing, focus grabbing, hovering, and scrolling with native UI signal emissions.
- [x] **Autonomous State Transition Waiting (`godot_wait_for_condition`)**: Polling/waiting engine for node existence, visibility, property equals, and arbitrary boolean expressions with configurable timeout.
- [x] **Multi-Property State Assertions (`godot_assert_node_state`)**: Structured assertion runner comparing expected vs actual runtime states for autonomous CI/E2E test validation.

### Phase 21: 3D GridMaps & Procedural Bezier Paths
- [x] **3D Voxel GridMap Engine (`godot_configure_gridmap`)**: Batch placement, clearing, mesh library assignment, cell sizing, orientations, and collision layer setup.
- [x] **Procedural Bezier Curve Geometry (`godot_create_curve_path`)**: Create 2D/3D bezier curves (Path2D/Path3D) with tangent handles, tilt angles, closed loop paths, and automatic child PathFollow attachments.

### Phase 22: Deep Profiling & Memory Leak Diagnostics
- [x] **Orphan Node Leak Detection (`godot_audit_orphan_nodes`)**: Deep inspection of unparented orphan nodes in memory (`Performance.RENDER_ORPHAN_NODES_IN_OBJECTS`) and active object lifecycle metrics.
- [x] **Multi-Frame Performance Profiler Trace (`godot_capture_profiler_trace`)**: Sampling engine measuring CPU process, physics process, navigation, draw calls, and memory telemetry.
- [x] **GPU VRAM Allocation Analyzer (`godot_inspect_vram_usage`)**: Video memory analyzer detailing texture memory, buffer memory, and active GPU budgets via `RenderingServer`.
























