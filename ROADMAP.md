# Godot MCP Roadmap

This roadmap documents the architectural gap analysis and planned feature evolution for `godot-mcp` relative to peer Game Engine and DCC MCP implementations (Unity MCP, Unreal Engine MCP, Blender MCP).

---

## 🎯 Capability Comparison & Target State

| Feature Area | Status | Target Capabilities |
|---|---|---|
| **Scene & Node Operations** | ✅ Completed | Node creation/modification/deletion, full property deserialization (`Vector2/3`, `Color`, `Resources`), Undo/Redo support, standalone scene creation (`godot_create_scene`), scene switching (`godot_open_scene`), real-time warning diagnostics. |
| **Engine Reflection & ClassDB** | 🔄 In Progress (Phase 1) | `godot_get_class_info`, `godot_get_documentation`, `godot_get_enum_constants`, eliminating LLM hallucinations across Godot 3 vs Godot 4 API changes. |
| **Shader & Material Authoring** | 🔄 In Progress (Phase 1/2) | `godot_validate_shader` (`.gdshader` compilation diagnostics), `godot_create_material` (`StandardMaterial3D`, `ShaderMaterial`, PBR properties). |
| **MCP Dynamic Resources & Prompts** | 📋 Planned (Phase 1) | Dynamic `godot://` URI resources (`godot://project/settings`, `godot://scene/active/tree`, `godot://engine/classes/{ClassName}`, `godot://logs/editor.log`) and workflow prompts (`prompt://fix-scene-warnings`, `prompt://create-rich-ui`). |
| **Asset & Reimport Pipeline** | 📋 Planned (Phase 2) | `godot_reimport_asset` (`.import` configuration, texture compression presets, pixel art settings), `godot_create_tileset`. |
| **Animation, Keyframes & Timeline** | 📋 Planned (Phase 3) | `godot_create_animation` (programmatic property tracks, transform tracks, method call tracks, easing curves, keyframes), `godot_configure_anim_tree`. |
| **Level Design & Geometry** | 📋 Planned (Phase 3) | `godot_tilemap_set_cells` (batch paint/erase cells on `TileMapLayer`), `godot_create_collision_polygon`, `godot_bake_navmesh` (`NavigationServer3D`/`2D`). |
| **GDScript Semantic LSP Integration** | 📋 Planned (Phase 3) | Connect directly to Godot's built-in LSP server (`port 6005`) for cross-file symbol definitions, references, and semantic renaming refactors. |
| **Runtime Profiler & Telemetry** | 📋 Planned (Phase 3) | `godot_get_performance_metrics` (`Performance.get_monitor()`: FPS, Draw Calls, VRAM, Objects), interactive Play Mode frame stepping. |

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
- [ ] **TileMapLayer Cell Painting (`godot_tilemap_set_cells`)**: Programmatically paint and query tile maps on Godot 4.7+ `TileMapLayer` nodes.

- [ ] **NavMesh Baking (`godot_bake_navmesh`)**: Trigger asynchronous navigation mesh baking on `NavigationRegion3D` / `NavigationRegion2D`.
- [ ] **Godot LSP Client (`port 6005`)**: Query symbols, definitions, find references, and perform safe cross-file renaming.
- [ ] **Performance Monitor Telemetry (`godot_get_performance_metrics`)**: Telemetry stream for draw calls, process frame time, physics tick time, and VRAM.
