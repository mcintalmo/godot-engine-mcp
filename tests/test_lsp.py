"""Unit and static analysis tests for Godot GDScript LSP client and tools."""

from pathlib import Path

import pytest

from godot_engine_mcp.client.lsp_client import GodotLSPClient
from godot_engine_mcp.config import GodotConfig
from godot_engine_mcp.models.lsp import (
    LSPQueryInput,
    LSPQueryType,
    LSPRenameInput,
)
from godot_engine_mcp.tools.lsp_tools import (
    handle_lsp_query,
    handle_lsp_rename,
)
from tests.test_tools import MockGodotClient


@pytest.mark.asyncio
async def test_lsp_tools_mock() -> None:
    """Test LSP tool handlers with MockGodotClient."""
    client = MockGodotClient()

    # 1. Query symbols
    res_syms = await handle_lsp_query(
        client,
        LSPQueryInput(
            file_path="res://scripts/player.gd", query_type=LSPQueryType.SYMBOLS
        ),
    )
    assert "Total Symbols" in res_syms
    assert "speed" in res_syms
    assert "_ready" in res_syms

    # 2. Query definition
    res_def = await handle_lsp_query(
        client,
        LSPQueryInput(
            file_path="res://scripts/player.gd",
            query_type=LSPQueryType.DEFINITION,
            line=12,
            character=15,
        ),
    )
    assert "Declared In" in res_def
    assert "Line 5" in res_def

    # 3. Query references
    res_refs = await handle_lsp_query(
        client,
        LSPQueryInput(
            file_path="res://scripts/player.gd",
            query_type=LSPQueryType.REFERENCES,
            line=5,
            character=5,
        ),
    )
    assert "Total References" in res_refs
    assert "res://scripts/player.gd:5" in res_refs
    assert "res://scripts/player.gd:12" in res_refs

    # 4. Query hover
    res_hover = await handle_lsp_query(
        client,
        LSPQueryInput(
            file_path="res://scripts/player.gd",
            query_type=LSPQueryType.HOVER,
            line=5,
            character=5,
        ),
    )
    assert "Movement speed in pixels per second." in res_hover

    # 5. Rename symbol
    res_rename = await handle_lsp_rename(
        client,
        LSPRenameInput(
            file_path="res://scripts/player.gd",
            line=5,
            character=5,
            new_name="move_speed",
        ),
    )
    assert "speed` -> `move_speed" in res_rename


@pytest.mark.asyncio
async def test_lsp_static_analysis_suite() -> None:
    """Test GodotLSPClient static analysis directly on temporary GDScript files."""
    tmp_proj = Path(__file__).parent / ".tmp_lsp_proj"
    tmp_proj.mkdir(exist_ok=True)
    try:
        (tmp_proj / "project.godot").write_text(
            'config_version=5\n[application]\nconfig/name="LSPTest"\n', encoding="utf-8"
        )
        scripts_dir = tmp_proj / "scripts"
        scripts_dir.mkdir(exist_ok=True)

        player_gd = scripts_dir / "player.gd"
        player_gd.write_text(
            """class_name Player
extends CharacterBody2D

signal health_depleted(final_amount: int)

## Movement speed in pixels per second.
var speed: float = 300.0
const MAX_HEALTH: int = 100

func _physics_process(delta: float) -> void:
    velocity = Vector2.RIGHT * speed
    move_and_slide()

func take_damage(amount: int) -> void:
    emit_signal("health_depleted", amount)
""",
            encoding="utf-8",
        )

        enemy_gd = scripts_dir / "enemy.gd"
        enemy_gd.write_text(
            """extends Node2D

func track_player(target: Player) -> void:
    var player_speed = target.speed
""",
            encoding="utf-8",
        )

        cfg = GodotConfig(executable_path=None, project_path=str(tmp_proj))
        lsp = GodotLSPClient(cfg)

        # 1. Test Static Symbols Query
        sym_res = await lsp.query("res://scripts/player.gd", query_type="symbols")
        assert sym_res.success is True
        sym_names = [s["name"] for s in sym_res.data["symbols"]]
        assert "Player" in sym_names
        assert "health_depleted" in sym_names
        assert "speed" in sym_names
        assert "MAX_HEALTH" in sym_names
        assert "_physics_process" in sym_names
        assert "take_damage" in sym_names

        # 2. Test Static Definition Lookup
        def_res = await lsp.query(
            "res://scripts/enemy.gd", query_type="definition", line=4, character=32
        )
        assert def_res.success is True
        assert def_res.data["definition"]["file"] == "res://scripts/player.gd"
        assert def_res.data["definition"]["line"] == 7

        # 3. Test Static References Search
        ref_res = await lsp.query(
            "res://scripts/player.gd", query_type="references", line=7, character=5
        )
        assert ref_res.success is True
        assert len(ref_res.data["references"]) >= 3

        # 4. Test Static Hover Docstring
        hov_res = await lsp.query(
            "res://scripts/player.gd", query_type="hover", line=7, character=5
        )
        assert hov_res.success is True
        assert (
            "Movement speed in pixels per second." in hov_res.data["hover"]["docstring"]
        )

        # 5. Test Static Cross-File Renaming
        ren_res = await lsp.rename(
            "res://scripts/player.gd", line=7, character=5, new_name="walk_speed"
        )
        assert ren_res.success is True
        assert len(ren_res.data["modified_files"]) == 2

        # Check modified contents
        new_player = player_gd.read_text(encoding="utf-8")
        assert "var walk_speed: float = 300.0" in new_player
        assert "Vector2.RIGHT * walk_speed" in new_player

        new_enemy = enemy_gd.read_text(encoding="utf-8")
        assert "var player_speed = target.walk_speed" in new_enemy

    finally:
        import shutil

        shutil.rmtree(tmp_proj, ignore_errors=True)
