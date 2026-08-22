"""Pydantic models for Godot Multiplayer Spawner & Network Synchronization."""

from pydantic import BaseModel, Field


class ReplicationPropertyConfig(BaseModel):
    """Configuration for a single synchronized property in SceneReplicationConfig."""

    path: str = Field(
        description="Node property path (e.g. ':position', ':rotation', 'HealthBar:value').",
    )
    spawn: bool = Field(
        default=True,
        description="Whether to replicate this property when spawning the node.",
    )
    sync: bool = Field(
        default=True,
        description="Whether to continuously synchronize this property across network frames.",
    )
    watch: bool = Field(
        default=False,
        description="Whether to sync only when the property value changes.",
    )


class ConfigureMultiplayerSpawnerInput(BaseModel):
    """Input model for godot_configure_multiplayer_spawner."""

    spawner_node_path: str = Field(
        description="Path to the MultiplayerSpawner node in the active scene.",
    )
    spawn_path: str | None = Field(
        default=None,
        description="Target node path where spawned nodes will be added (e.g. '../Entities').",
    )
    spawn_limit: int | None = Field(
        default=None,
        description="Maximum number of nodes allowed to be spawned at once (0 for unlimited).",
    )
    spawnable_scenes: list[str] | None = Field(
        default=None,
        description="List of resource paths to scenes that can be spawned (e.g. ['res://player.tscn']).",
    )
    clear_spawnable_scenes: bool = Field(
        default=False,
        description="Whether to clear existing spawnable scenes before adding new ones.",
    )


class ConfigureMultiplayerSynchronizerInput(BaseModel):
    """Input model for godot_configure_multiplayer_synchronizer."""

    synchronizer_node_path: str = Field(
        description="Path to the MultiplayerSynchronizer node in the active scene.",
    )
    root_path: str | None = Field(
        default=None,
        description="Node path relative to which properties will be resolved (e.g. '..' or '.').",
    )
    replication_interval: float | None = Field(
        default=None,
        description="Interval in seconds between sync replication packets (0 for every frame).",
    )
    properties: list[ReplicationPropertyConfig] | None = Field(
        default=None,
        description="List of properties to configure for replication in SceneReplicationConfig.",
    )
    visibility_update_mode: str | None = Field(
        default=None,
        description="Visibility update mode: 'always', 'visible', or 'never'.",
    )
    clear_properties: bool = Field(
        default=False,
        description="Whether to clear existing properties from the replication config.",
    )


class SimulateNetworkConditionsInput(BaseModel):
    """Input model for godot_simulate_network_conditions."""

    latency_ms: int = Field(
        default=0,
        description="Simulated round-trip latency in milliseconds.",
    )
    packet_loss_percent: float = Field(
        default=0.0,
        description="Simulated packet drop rate percentage (0.0 to 100.0).",
    )
    jitter_ms: int = Field(
        default=0,
        description="Simulated latency jitter variance in milliseconds.",
    )
    offline_mode: bool = Field(
        default=False,
        description="Whether to simulate a complete network disconnect / offline state.",
    )
