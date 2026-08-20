"""Tool handlers for Godot Node signals and connection wiring."""

from godot_mcp.client.base import GodotClient
from godot_mcp.models.signal_wire import (
    ConnectSignalInput,
    GetNodeSignalsInput,
    GetSignalConnectionsInput,
)
from godot_mcp.tools.formatters import format_result


async def handle_get_node_signals(
    client: GodotClient,
    params: GetNodeSignalsInput,
) -> str:
    """Handle godot_get_node_signals tool execution."""
    result = await client.get_node_signals(
        node_path=params.node_path,
        include_inherited=params.include_inherited,
    )
    return format_result(result)


async def handle_connect_signal(
    client: GodotClient,
    params: ConnectSignalInput,
) -> str:
    """Handle godot_connect_signal tool execution."""
    result = await client.connect_signal(
        source_node_path=params.source_node_path,
        signal_name=params.signal_name,
        target_node_path=params.target_node_path,
        method_name=params.method_name,
        disconnect=params.disconnect,
        persist=params.persist,
        one_shot=params.one_shot,
        deferred=params.deferred,
    )
    return format_result(result)


async def handle_get_signal_connections(
    client: GodotClient,
    params: GetSignalConnectionsInput,
) -> str:
    """Handle godot_get_signal_connections tool execution."""
    result = await client.get_signal_connections(
        node_path=params.node_path,
        signal_name=params.signal_name,
        incoming=params.incoming,
        outgoing=params.outgoing,
    )
    return format_result(result)
