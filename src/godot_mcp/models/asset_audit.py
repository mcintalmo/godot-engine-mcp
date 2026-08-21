"""Pydantic models for Godot Project Asset Audit, Orphan Cleanup, and Texture Inspection."""

from pydantic import BaseModel, Field


class AuditAssetsInput(BaseModel):
    """Input model for godot_audit_assets."""

    include_extensions: list[str] | None = Field(
        default=None,
        description="Optional list of file extensions to include in audit (e.g. ['.tscn', '.tres', '.png', '.wav', '.gd']). Defaults to all game assets.",
    )
    ignore_paths: list[str] | None = Field(
        default=None,
        description="Optional list of path prefixes to ignore during the audit (e.g. ['res://addons/']).",
    )


class CleanOrphansInput(BaseModel):
    """Input model for godot_clean_orphans."""

    file_paths: list[str] | None = Field(
        default=None,
        description="Specific orphan file paths to clean. If None or empty, scans project and targets all detected orphan assets.",
    )
    dry_run: bool = Field(
        default=True,
        description="If True, simulates cleanup and returns the candidate files without modifying or deleting anything on disk.",
    )
    quarantine_folder: str | None = Field(
        default=None,
        description="Optional quarantine folder path (e.g. 'res://.quarantine/') to move files into instead of permanent deletion.",
    )


class GetTextureInfoInput(BaseModel):
    """Input model for godot_get_texture_info."""

    texture_path: str = Field(
        description="Path to the texture file in the project (e.g. 'res://icon.svg' or 'res://textures/diffuse.png').",
    )
