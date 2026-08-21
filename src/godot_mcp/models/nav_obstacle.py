"""Pydantic models for Godot 2D/3D Navigation Obstacles and Avoidance."""

from pydantic import BaseModel, Field


class ConfigureNavigationObstacleInput(BaseModel):
    """Input model for godot_configure_navigation_obstacle."""

    node_path: str | None = Field(
        default=None,
        description="Path to an existing NavigationObstacle2D/3D node in the active scene, or None to create a new one.",
    )
    parent_path: str | None = Field(
        default=None,
        description="Parent node path if creating a new obstacle (defaults to edited scene root).",
    )
    node_name: str = Field(
        default="NavigationObstacle3D",
        description="Name of the obstacle node.",
    )
    is_3d: bool = Field(
        default=True,
        description="True to create/configure NavigationObstacle3D, False for NavigationObstacle2D.",
    )
    radius: float = Field(
        default=1.0,
        description="Avoidance radius for dynamic obstacle avoidance (bubbles). Set to 0.0 if using static polygon vertices.",
    )
    velocity: list[float] | None = Field(
        default=None,
        description="Optional current velocity vector ([vx, vy, vz] for 3D, [vx, vy] for 2D) for RVO velocity prediction.",
    )
    vertices: list[list[float]] | None = Field(
        default=None,
        description="Optional list of 2D/3D point coordinates defining a static polygon boundary obstacle.",
    )
    avoidance_layers: int = Field(
        default=1,
        description="Avoidance layers bitmask (integer).",
    )
    affect_navigation_mesh: bool = Field(
        default=False,
        description="Whether this obstacle affects navigation mesh baking.",
    )
    carve_navigation_mesh: bool = Field(
        default=False,
        description="Whether this obstacle carves a hole into navigation mesh baking.",
    )
