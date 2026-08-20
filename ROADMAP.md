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
- [ ] **Interactive Play Mode & Debug Control (`godot_pause_game`, `godot_resume_game`, `godot_step_frame`)**: Pause, unpause, step single physics/process frames, and inspect live runtime trees.
- [ ] **Audio Bus & Effect Pipeline (`godot_configure_audio_bus`, `godot_set_bus_effect`)**: Programmatically configure `AudioServer` layout, routing, bus volumes, and audio effects (Reverb, EQ, Chorus).




