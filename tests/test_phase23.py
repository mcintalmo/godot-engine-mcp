"""Unit and headless tests for Godot Phase 23 tools (Multiplayer Spawner & Network Synchronization)."""

import pytest

from godot_mcp.client.headless_cli import HeadlessCLIClient
from godot_mcp.config import GodotConfig
from godot_mcp.models.multiplayer import (
    ConfigureMultiplayerSpawnerInput,
    ConfigureMultiplayerSynchronizerInput,
    ReplicationPropertyConfig,
    SimulateNetworkConditionsInput,
)
from godot_mcp.tools.multiplayer_tools import (
    handle_configure_multiplayer_spawner,
    handle_configure_multiplayer_synchronizer,
    handle_simulate_network_conditions,
)
from tests.test_tools import MockGodotClient


@pytest.mark.asyncio
async def test_phase23_tools_mock() -> None:
    """Test Phase 23 tools with MockGodotClient."""
    client = MockGodotClient()

    # 1. Configure Multiplayer Spawner
    spawner_res = await handle_configure_multiplayer_spawner(
        client,
        ConfigureMultiplayerSpawnerInput(
            spawner_node_path="World/EntitySpawner",
            spawn_path="../Entities",
            spawn_limit=64,
            spawnable_scenes=["res://player.tscn", "res://enemy.tscn"],
        ),
    )
    assert "Configured MultiplayerSpawner" in spawner_res
    assert "EntitySpawner" in spawner_res
    assert "Added 2 spawnable scenes" in spawner_res

    # 2. Configure Multiplayer Synchronizer
    sync_res = await handle_configure_multiplayer_synchronizer(
        client,
        ConfigureMultiplayerSynchronizerInput(
            synchronizer_node_path="Player/Synchronizer",
            root_path="..",
            replication_interval=0.033,
            properties=[
                ReplicationPropertyConfig(path=":position", spawn=True, sync=True),
                ReplicationPropertyConfig(path=":rotation", spawn=True, sync=True),
                ReplicationPropertyConfig(
                    path="HealthBar:value", spawn=True, sync=False, watch=True
                ),
            ],
        ),
    )
    assert "Configured MultiplayerSynchronizer" in sync_res
    assert "Synchronizer" in sync_res
    assert "Configured 3 replication properties" in sync_res

    # 3. Simulate Network Conditions
    net_res = await handle_simulate_network_conditions(
        client,
        SimulateNetworkConditionsInput(
            latency_ms=120,
            packet_loss_percent=2.5,
            jitter_ms=15,
            offline_mode=False,
        ),
    )
    assert "Simulated Network Profile" in net_res
    assert "SIMULATION_ACTIVE" in net_res
    assert "120 ms" in net_res
    assert "2.5%" in net_res


@pytest.mark.asyncio
async def test_phase23_headless_client(tmp_path: pytest.TempPathFactory) -> None:
    """Test Phase 23 tools with HeadlessCLIClient."""
    cfg = GodotConfig(project_path=str(tmp_path))
    client = HeadlessCLIClient(cfg)

    # 1. Configure Multiplayer Spawner headlessly
    spawner_res = await handle_configure_multiplayer_spawner(
        client,
        ConfigureMultiplayerSpawnerInput(
            spawner_node_path="MultiplayerSpawner",
            spawnable_scenes=["res://coin.tscn"],
        ),
    )
    assert "Configured MultiplayerSpawner" in spawner_res

    # 2. Configure Multiplayer Synchronizer headlessly
    sync_res = await handle_configure_multiplayer_synchronizer(
        client,
        ConfigureMultiplayerSynchronizerInput(
            synchronizer_node_path="MultiplayerSynchronizer",
            properties=[ReplicationPropertyConfig(path=":position")],
        ),
    )
    assert "Configured MultiplayerSynchronizer" in sync_res

    # 3. Simulate Network Conditions headlessly
    net_res = await handle_simulate_network_conditions(
        client,
        SimulateNetworkConditionsInput(offline_mode=True),
    )
    assert "Simulated Network Profile" in net_res
    assert "Offline Mode" in net_res
    assert "True" in net_res
