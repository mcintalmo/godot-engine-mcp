"""Tool handlers for Godot Localization and Translation management."""

from godot_mcp.client.base import GodotClient
from godot_mcp.models.localization import (
    AddTranslationInput,
    GetTranslationsInput,
)
from godot_mcp.tools.formatters import format_result


async def handle_get_translations(
    client: GodotClient,
    params: GetTranslationsInput,
) -> str:
    """Handle godot_get_translations tool execution."""
    result = await client.get_translations(
        locale_filter=params.locale_filter,
    )
    return format_result(result)


async def handle_add_translation(
    client: GodotClient,
    params: AddTranslationInput,
) -> str:
    """Handle godot_add_translation tool execution."""
    result = await client.add_translation(
        translation_path=params.translation_path,
        test_locale=params.test_locale,
    )
    return format_result(result)
