"""Unit and headless integration tests for Godot Theme and UI styling tools."""

from pathlib import Path

import pytest

from godot_mcp.client.headless_cli import HeadlessCLIClient
from godot_mcp.config import GodotConfig
from godot_mcp.models.theme import (
    ApplyThemeOverrideInput,
    CreateThemeInput,
    StyleBoxFlatConfig,
    ThemeOverrideType,
)
from godot_mcp.tools.theme_tools import (
    handle_apply_theme_override,
    handle_create_theme,
)
from tests.test_tools import MockGodotClient


@pytest.mark.asyncio
async def test_theme_tools_mock() -> None:
    """Test theme tool handlers with MockGodotClient."""
    client = MockGodotClient()

    # 1. Create Theme with custom styles, colors, and constants
    create_res = await handle_create_theme(
        client,
        CreateThemeInput(
            save_path="res://themes/dark_modern.tres",
            base_font_size=16,
            colors={
                "Button": {"font_color": "#ffffff", "font_hover_color": "#7aa2f7"},
                "Label": {"font_color": "#c0caf5"},
            },
            constants={"VBoxContainer": {"separation": 12}},
            styleboxes={
                "Button": {
                    "normal": StyleBoxFlatConfig(
                        bg_color="#1e1e2e",
                        border_color="#7aa2f7",
                        border_width=2,
                        corner_radius=6,
                        content_margins=[12, 8, 12, 8],
                    ),
                    "hover": StyleBoxFlatConfig(
                        bg_color="#282a36",
                        border_color="#bb9af7",
                        border_width=2,
                        corner_radius=6,
                    ),
                }
            },
            apply_to_node_path="CanvasLayer/MainMenu",
        ),
    )
    assert "Theme Resource" in create_res
    assert "res://themes/dark_modern.tres" in create_res
    assert "16 px" in create_res
    assert "Button" in create_res
    assert "CanvasLayer/MainMenu" in create_res

    # 2. Apply theme override to a Control node
    override_res = await handle_apply_theme_override(
        client,
        ApplyThemeOverrideInput(
            node_path="CanvasLayer/MainMenu/StartButton",
            override_type=ThemeOverrideType.STYLEBOX,
            item_name="normal",
            value=StyleBoxFlatConfig(
                bg_color="#181825",
                corner_radius=8,
            ),
        ),
    )
    assert "StartButton" in override_res
    assert "stylebox" in override_res
    assert "normal" in override_res
    assert "bg_color" in override_res


@pytest.mark.asyncio
async def test_create_theme_headless() -> None:
    """Test creating and saving a Godot Theme resource headlessly with Godot CLI."""
    exe = GodotConfig.discover_executable()
    if not exe:
        pytest.skip("Godot executable not available.")

    tmp_proj = Path(__file__).parent / ".tmp_theme_proj"
    tmp_proj.mkdir(exist_ok=True)
    try:
        (tmp_proj / "project.godot").write_text(
            'config_version=5\n[application]\nconfig/name="ThemeTest"\n',
            encoding="utf-8",
        )
        cfg = GodotConfig(executable_path=exe, project_path=str(tmp_proj))
        client = HeadlessCLIClient(cfg)

        res = await handle_create_theme(
            client,
            CreateThemeInput(
                save_path="res://themes/custom_ui.tres",
                base_font_size=18,
                colors={"Button": {"font_color": "#ffffff"}},
                constants={"VBoxContainer": {"separation": 16}},
                styleboxes={
                    "Button": {
                        "normal": StyleBoxFlatConfig(
                            bg_color="#24283b",
                            border_color="#7aa2f7",
                            border_width=2,
                            corner_radius=8,
                        )
                    }
                },
            ),
        )
        assert "Theme Resource" in res or "Theme" in res

        theme_file = tmp_proj / "themes" / "custom_ui.tres"

        assert theme_file.exists()
        content = theme_file.read_text(encoding="utf-8")
        assert "Theme" in content
        assert "StyleBoxFlat" in content
    finally:
        import shutil

        shutil.rmtree(tmp_proj, ignore_errors=True)
