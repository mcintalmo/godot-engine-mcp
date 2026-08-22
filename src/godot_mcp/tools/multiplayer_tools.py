"""Tool handlers for Godot Multiplayer Spawner & Network Synchronization."""

from godot_mcp.client.base import GodotClient
from godot_mcp.models.multiplayer import (
    ConfigureMultiplayerSpawnerInput,
    ConfigureMultiplayerSynchronizerInput,
    SimulateNetworkConditionsInput,
)
from godot_mcp.tools.formatters import format_result


async def handle_configure_multiplayer_spawner(
    client: GodotClient,
    params: ConfigureMultiplayerSpawnerInput,
) -> str:
    """Handle godot_configure_multiplayer_spawner tool execution."""
    result = await client.configure_multiplayer_spawner(
        spawner_node_path=params.spawner_node_path,
        spawn_path=params.spawn_path,
        spawn_limit=params.spawn_limit,
        spawnable_scenes=params.spawnable_scenes,
        clear_spawnable_scenes=params.clear_spawnable_scenes,
    )
    return format_result(result)


async def handle_configure_multiplayer_synchronizer(
    client: GodotClient,
    params: ConfigureMultiplayerSynchronizerInput,
) -> str:
    """Handle godot_configure_multiplayer_synchronizer tool execution."""
    result = await client.configure_multiplayer_synchronizer(
        synchronizer_node_path=params.synchronizer_node_path,
        root_path=params.root_path,
        replication_interval=params.replication_interval,
        properties=[p.model_dump() for p in params.properties]
        if params.properties
        else None,
        visibility_update_mode=params.visibility_update_mode,
        clear_properties=params.clear_properties,
    )
    return format_result(result)


async def handle_simulate_network_conditions(
    client: GodotClient,
    params: SimulateNetworkConditionsInput,
) -> str:
    """Handle godot_simulate_network_conditions tool execution."""
    result = await client.simulate_network_conditions(
        latency_ms=params.latency_ms,
        packet_loss_percent=params.packet_loss_percent,
        jitter_ms=params.jitter_ms,
        offline_mode=params.offline_mode,
    )
    return format_result(result)
