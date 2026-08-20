"""Pydantic models for NavMesh baking and NavigationRegion management."""

from enum import Enum

from pydantic import BaseModel, Field


class NavDimension(str, Enum):
    """Navigation space dimension."""

    TWO_D = "2D"
    THREE_D = "3D"


class BakeNavMeshInput(BaseModel):
    """Input model for godot_bake_navmesh."""

    node_path: str = Field(
        ...,
        description="Target NavigationRegion3D or NavigationRegion2D node path in the active scene (e.g. 'NavigationRegion3D' or 'World/NavRegion').",
    )
    dimension: NavDimension = Field(
        default=NavDimension.THREE_D,
        description="Navigation dimension ('2D' or '3D').",
    )
    on_thread: bool = Field(
        default=True,
        description="Whether to bake the navigation mesh asynchronously on a worker thread.",
    )
    agent_radius: float | None = Field(
        default=None,
        description="Radius of the navigation agent in world units.",
    )
    agent_height: float | None = Field(
        default=None,
        description="Height of the navigation agent in world units (3D only).",
    )
    agent_max_climb: float | None = Field(
        default=None,
        description="Maximum step height the navigation agent can climb over (3D only).",
    )
    agent_max_slope: float | None = Field(
        default=None,
        description="Maximum walkable slope in degrees (3D only).",
    )
    cell_size: float | None = Field(
        default=None,
        description="Rasterization cell size for voxel / polygon generation.",
    )
    cell_height: float | None = Field(
        default=None,
        description="Rasterization cell height for voxel generation (3D only).",
    )
    save_navmesh_path: str | None = Field(
        default=None,
        description="Optional path to save the configured / baked NavigationMesh resource (.tres).",
    )


class CreateNavigationRegionInput(BaseModel):
    """Input model for godot_create_navigation_region."""

    name: str = Field(
        default="NavigationRegion3D",
        description="Name of the NavigationRegion node to create.",
    )
    dimension: NavDimension = Field(
        default=NavDimension.THREE_D,
        description="Navigation dimension ('2D' or '3D').",
    )
    parent_node_path: str = Field(
        default=".",
        description="Target parent node path in the active scene (e.g. '.' or 'World').",
    )
    navmesh_path: str | None = Field(
        default=None,
        description="Optional path to an existing NavigationMesh or NavigationPolygon resource file (.tres).",
    )
