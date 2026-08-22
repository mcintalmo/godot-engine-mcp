"""Pydantic models for Godot Deep Profiling & Memory Leak Diagnostics."""

from pydantic import BaseModel, Field


class AuditOrphanNodesInput(BaseModel):
    """Input model for godot_audit_orphan_nodes."""

    print_orphans_to_stdout: bool = Field(
        default=False,
        description="Whether to call Node.print_orphan_nodes() in engine stdout.",
    )


class CaptureProfilerTraceInput(BaseModel):
    """Input model for godot_capture_profiler_trace."""

    frames_to_sample: int = Field(
        default=10,
        description="Number of engine frames to sample for computing min/max/average execution times.",
    )


class InspectVRAMUsageInput(BaseModel):
    """Input model for godot_inspect_vram_usage."""

    detailed: bool = Field(
        default=True,
        description="Whether to include granular breakdowns for texture, buffer, and video memory.",
    )
