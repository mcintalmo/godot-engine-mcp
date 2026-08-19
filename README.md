# Godot MCP

A modern, high-quality Model Context Protocol (MCP) server for the **Godot Engine 4.7+**.

Built with the official **Python MCP SDK v2.0+** (`mcp>=2.0.0`, FastMCP, 2026-07-28 stateless protocol), strict Pydantic v2 schemas, type safety via Astral `ty`, and a robust **dual-tier hybrid bridge** architecture inspired by the Unity MCP philosophy.

---

## Architecture Overview

Godot MCP operates across two complementary layers:

1. **Live Editor Bridge (`addons/godot_mcp/`)**:
   A modular GDScript `EditorPlugin` running inside Godot that hosts a local WebSocket IPC server (`ws://127.0.0.1:3118/ws`). It provides live access to:
   - `EditorInterface` and active scene tree hierarchy
   - Interactive node creation and modification with full `EditorUndoRedoManager` support
   - Signal wiring and script attachment
   - High-fidelity 2D/3D viewport screenshot capture for multimodal models

2. **Headless CLI Fallback (`godot --headless`)**:
   When the Godot Editor is not open, the server seamlessly executes offline operations via the Godot binary:
   - GDScript syntax validation and compilation diagnostics (`godot --check-only`)
   - `project.godot` settings reading and modification
   - Project file and resource discovery (`res://` asset queries)
   - Subprocess project execution and headless test suite running

```
┌────────────────────────────────────────────────────────┐
│                      AI Client                         │
│         (Cursor / Claude / Gemini / Antigravity)       │
└───────────────────────────┬────────────────────────────┘
                            │ MCP (stdio / HTTP)
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
```

---

## Tool Catalog

All tools adhere to MCP best practices, providing clear docstrings, Pydantic v2 validation, dual formatting (`markdown` and `json`), and explicit tool annotations (`read_only_hint`, `destructive_hint`, `idempotent_hint`, `open_world_hint`).

### Project & Version Management
- `godot_get_version`: Probes engine version, build type, active project, and connection mode.
- `godot_get_project_settings`: Queries configuration settings from `project.godot` (e.g. window size, autoloads).
- `godot_set_project_setting`: Writes or updates configuration values in `project.godot`.
- `godot_list_project_files`: Searches project assets, scenes (`.tscn`), scripts (`.gd`), and textures (`res://`).

### Scene & Node Hierarchy
- `godot_list_nodes`: Traverses the active scene tree with configurable depth.
- `godot_get_node`: Inspects node properties, attached scripts, transforms, and signals.
- `godot_create_node`: Adds a node of any Godot class (e.g., `CharacterBody2D`, `Camera3D`, `Control`) with initial properties.
- `godot_modify_node`: Updates properties on existing nodes with Undo/Redo history.
- `godot_delete_node`: Safely removes a node from the active scene.
- `godot_connect_signal`: Connects signals between nodes and target handler methods.
- `godot_instantiate_scene`: Instantiates `.tscn` packed scene files into the active scene.
- `godot_save_scene`: Saves the active scene or exports to a target `.tscn` file.

### Scripting & Validation
- `godot_validate_script`: Checks GDScript code or files for syntax errors and compilation diagnostics.
- `godot_create_script`: Creates or updates GDScript source files and optionally attaches them to scene nodes.

### Debugging, Testing & Vision
- `godot_run_project`: Launches the game project in debug mode and captures execution logs/errors.
- `godot_run_tests`: Executes headless test suites and parses test outcomes.
- `godot_take_screenshot`: Captures active 2D/3D viewport or running game framebuffer for multimodal visual analysis.

---

## Quick Start

### 1. Requirements
- Python 3.14+ managed with `uv`
- Godot Engine 4.7+ (or 4.7.1+)

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/your-org/godot-mcp.git
cd godot-mcp

# Sync environment with uv
uv sync
```

### 3. Setup a Project

```bash
# Install and auto-enable the addon into your project:
uv run godot-mcp install-addon /path/to/your/godot/project

# Launch or open the Godot Editor from CLI:
uv run godot-mcp open-editor /path/to/your/godot/project

# Reload the active running Godot Editor:
uv run godot-mcp reload /path/to/your/godot/project
```

### 4. Running the MCP Server

```bash
# Standard stdio mode for AI assistants
uv run godot-mcp run

# Check environment and Godot discovery
uv run godot-mcp version

# Probe live editor bridge and CLI status
uv run godot-mcp probe
```


### 5. Configuring with AI Clients

#### Claude Desktop / Claude Code
Add to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "godot": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/godot-mcp",
        "run",
        "godot-mcp"
      ],
      "env": {
        "GODOT_PROJECT_PATH": "/path/to/your/godot/project"
      }
    }
  }
}
```

---

## Development & Verification

```bash
# Run test suite
uv run pytest --cov=godot_mcp

# Run static type checker
uv run ty check

# Run linter and formatter
uv run ruff check && uv run ruff format
```
