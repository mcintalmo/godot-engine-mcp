"""Pydantic models for Godot TileSet Terrain and Autotiling configuration."""

from typing import Any

from pydantic import BaseModel, Field


class ConfigureTileSetTerrainInput(BaseModel):
    """Input model for godot_configure_tileset_terrain."""

    tileset_path: str = Field(
        description="Path to the TileSet (.tres) resource file or scene node holding a TileSet (e.g. 'res://tilesets/dungeon.tres' or 'TileMapLayer').",
    )
    terrain_set: int = Field(
        default=0,
        description="Terrain set index to configure (creates if doesn't exist).",
    )
    mode: str = Field(
        default="match_corners_and_sides",
        description="Terrain mode: 'match_corners_and_sides', 'match_corners', or 'match_sides'.",
    )
    terrains: list[dict[str, Any]] | None = Field(
        default=None,
        description="List of terrain definitions, each with 'name' and optional 'color' (e.g. [{'name': 'Grass', 'color': '#228B22'}, {'name': 'Water', 'color': '#1E90FF'}]).",
    )
    tile_peering_bits: list[dict[str, Any]] | None = Field(
        default=None,
        description="Optional list of tile peering bit assignments for autotiling, each containing 'source_id', 'atlas_coords' ([x, y]), optional 'terrain' (int), and 'bits' (dict of bit name to terrain index).",
    )
    save_path: str | None = Field(
        default=None,
        description="Optional custom destination path to save the modified TileSet resource.",
    )
