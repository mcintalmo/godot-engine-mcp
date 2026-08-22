"""Tool handlers for Godot AudioServer bus and effect pipeline."""

from godot_engine_mcp.client.base import GodotClient
from godot_engine_mcp.models.audio import (
    ConfigureAudioBusInput,
    GetAudioLayoutInput,
    SetBusEffectInput,
)
from godot_engine_mcp.tools.formatters import format_result


async def handle_get_audio_layout(
    client: GodotClient,
    params: GetAudioLayoutInput,
) -> str:
    """Handle godot_get_audio_layout tool execution."""
    result = await client.get_audio_layout(
        include_effects=params.include_effects,
    )
    return format_result(result)


async def handle_configure_audio_bus(
    client: GodotClient,
    params: ConfigureAudioBusInput,
) -> str:
    """Handle godot_configure_audio_bus tool execution."""
    result = await client.configure_audio_bus(
        bus_name=params.bus_name,
        create_if_missing=params.create_if_missing,
        volume_db=params.volume_db,
        volume_linear=params.volume_linear,
        send_to_bus=params.send_to_bus,
        mute=params.mute,
        solo=params.solo,
        bypass_effects=params.bypass_effects,
        save_layout_path=params.save_layout_path,
    )
    return format_result(result)


async def handle_set_bus_effect(
    client: GodotClient,
    params: SetBusEffectInput,
) -> str:
    """Handle godot_set_bus_effect tool execution."""
    result = await client.set_bus_effect(
        bus_name=params.bus_name,
        effect_type=params.effect_type,
        effect_index=params.effect_index,
        enabled=params.enabled,
        properties=params.properties,
        save_layout_path=params.save_layout_path,
    )
    return format_result(result)
