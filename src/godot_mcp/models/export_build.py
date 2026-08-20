"""Pydantic models for Godot project export presets and build pipelines."""

from pydantic import BaseModel, Field


class GetExportPresetsInput(BaseModel):
    """Input model for godot_get_export_presets."""


class ExportProjectInput(BaseModel):
    """Input model for godot_export_project."""

    preset_name: str = Field(
        description="Name of the export preset defined in export_presets.cfg (e.g. 'Windows Desktop', 'Linux', 'Web', 'macOS').",
    )
    output_path: str = Field(
        description="Destination path for the exported binary or package (e.g. 'builds/game.exe', 'builds/web/index.html').",
    )
    debug: bool = Field(
        default=False,
        description="If true, exports a debug build with symbol logging. Defaults to release build.",
    )
