"""Pydantic models for Godot Node signals and event connection wiring."""

from pydantic import BaseModel, Field


class GetNodeSignalsInput(BaseModel):
    """Input model for godot_get_node_signals."""

    node_path: str = Field(
        description="Path of the target node in the active scene (e.g. 'Player', 'Button', 'Enemy/Area3D').",
    )
    include_inherited: bool = Field(
        default=True,
        description="Whether to include inherited base class signals (e.g. Node, CanvasItem, Object).",
    )


class ConnectSignalInput(BaseModel):
    """Input model for godot_connect_signal."""

    source_node_path: str = Field(
        description="Path of the emitting source node in the active scene.",
    )
    signal_name: str = Field(
        description="Name of the signal to connect or disconnect (e.g. 'pressed', 'body_entered', 'timeout').",
    )
    target_node_path: str = Field(
        description="Path of the receiving target node in the active scene.",
    )
    method_name: str = Field(
        description="Name of the target method / callable to invoke on signal emission (e.g. '_on_button_pressed').",
    )
    disconnect: bool = Field(
        default=False,
        description="If true, disconnects the existing signal connection instead of connecting it.",
    )
    persist: bool = Field(
        default=True,
        description="If true, marks connection with CONNECT_PERSIST so it serializes into the .tscn scene file.",
    )
    one_shot: bool = Field(
        default=False,
        description="If true, automatically disconnects the signal after firing once (CONNECT_ONE_SHOT).",
    )
    deferred: bool = Field(
        default=False,
        description="If true, defers the method invocation until idle time (CONNECT_DEFERRED).",
    )


class GetSignalConnectionsInput(BaseModel):
    """Input model for godot_get_signal_connections."""

    node_path: str = Field(
        description="Path of the target node in the active scene to inspect connections for.",
    )
    signal_name: str | None = Field(
        default=None,
        description="Optional filter for a specific signal name.",
    )
    incoming: bool = Field(
        default=True,
        description="Include incoming connections targeting this node.",
    )
    outgoing: bool = Field(
        default=True,
        description="Include outgoing connections emitted by this node.",
    )
