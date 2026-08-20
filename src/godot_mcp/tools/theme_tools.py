"""Tool handlers for Godot Theme creation and Control node style overrides."""

from typing import Any

from godot_mcp.client.base import GodotClient
from godot_mcp.models.theme import (
    ApplyThemeOverrideInput,
    CreateThemeInput,
)
from godot_mcp.tools.formatters import format_result


async def handle_create_theme(
    client: GodotClient,
    params: CreateThemeInput,
) -> str:
    """Handle godot_create_theme tool execution."""
    raw_styleboxes: dict[str, dict[str, Any]] = {}
    if params.styleboxes:
        for node_type, boxes in params.styleboxes.items():
            raw_styleboxes[node_type] = {}
            for name, cfg in boxes.items():
                raw_styleboxes[node_type][name] = cfg.model_dump(exclude_none=True)

    result = await client.create_theme(
        save_path=params.save_path,
        base_font_path=params.base_font_path,
        base_font_size=params.base_font_size,
        colors=params.colors,
        constants=params.constants,
        styleboxes=raw_styleboxes if raw_styleboxes else None,
        apply_to_node_path=params.apply_to_node_path,
    )
    return format_result(result)


async def handle_apply_theme_override(
    client: GodotClient,
    params: ApplyThemeOverrideInput,
) -> str:
    """Handle godot_apply_theme_override tool execution."""
    val = params.value
    if hasattr(val, "model_dump"):
        val = val.model_dump(exclude_none=True)

    result = await client.apply_theme_override(
        node_path=params.node_path,
        override_type=params.override_type.value,
        item_name=params.item_name,
        value=val,
    )
    return format_result(result)
