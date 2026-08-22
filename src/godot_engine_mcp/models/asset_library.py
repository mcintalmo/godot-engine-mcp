"""Data models and Pydantic schemas for the Godot Asset Library integration."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from godot_engine_mcp.models.common import ResponseFormat


class AssetCategory(StrEnum):
    """Categories available in the Godot Asset Library."""

    ANY = "any"
    TWO_D_TOOLS = "2d_tools"
    THREE_D_TOOLS = "3d_tools"
    SHADERS = "shaders"
    MATERIALS = "materials"
    SCRIPTS = "scripts"
    MISC = "misc"
    TEMPLATES = "templates"


class AssetSort(StrEnum):
    """Sorting criteria for Asset Library queries."""

    UPDATED = "updated"
    RATING = "rating"
    NAME = "name"
    COST = "cost"


class SearchAssetLibraryInput(BaseModel):
    """Input parameters for searching the Godot Asset Library."""

    query: str | None = Field(
        None,
        description="Search term/keyword to filter assets (e.g. 'phantom camera', 'dialogue', 'jolt', 'gut').",
    )
    category: str | None = Field(
        None,
        description="Category filter (e.g. '2d_tools', '3d_tools', 'shaders', 'materials', 'scripts', 'misc', 'templates').",
    )
    godot_version: str | None = Field(
        None,
        description="Target Godot version filter (e.g. '4.x', '4.3', '4.4', '4.7'). Defaults to engine version.",
    )
    sort_by: AssetSort = Field(
        AssetSort.UPDATED,
        description="Sorting order for search results.",
    )
    max_results: int = Field(
        10,
        ge=1,
        le=50,
        description="Maximum number of search results to return (1-50).",
    )
    response_format: ResponseFormat = Field(
        ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for formatted summary or 'json' for raw structured data.",
    )


class GetAssetDetailsInput(BaseModel):
    """Input parameters for retrieving full details of a Godot Asset."""

    asset_id: str = Field(
        ...,
        description="Unique identifier of the asset in the Godot Asset Library (e.g. '1234').",
    )
    response_format: ResponseFormat = Field(
        ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for formatted summary or 'json' for raw structured data.",
    )


class InstallAssetPackageInput(BaseModel):
    """Input parameters for downloading and installing an asset package into a Godot project."""

    asset_id: str | None = Field(
        None,
        description="Asset Library ID to fetch and install. Required if download_url is not provided.",
    )
    download_url: str | None = Field(
        None,
        description="Direct ZIP archive URL of the asset/addon to download and install. If provided, overrides asset_id.",
    )
    target_dir: str = Field(
        "res://addons",
        description="Target installation path inside project (defaults to 'res://addons').",
    )
    auto_enable_plugin: bool = Field(
        True,
        description="If True and the package contains a Godot editor plugin (plugin.cfg), auto-registers it in project.godot.",
    )
    response_format: ResponseFormat = Field(
        ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for formatted summary or 'json' for raw structured data.",
    )


class AssetItem(BaseModel):
    """Summary record of an asset item from the Godot Asset Library."""

    asset_id: str
    title: str
    author: str
    author_id: str | None = None
    version_string: str = ""
    godot_version: str = ""
    category: str = ""
    cost: str = ""
    support_level: str = "community"
    download_url: str = ""
    icon_url: str | None = None
    description: str = ""
    raw_data: dict[str, Any] = Field(default_factory=dict)
