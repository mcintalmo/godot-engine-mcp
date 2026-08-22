"""Pydantic models for Godot Performance Monitor telemetry."""

from enum import Enum

from pydantic import BaseModel, Field


class MetricCategory(str, Enum):
    """Categories of performance telemetry metrics."""

    ALL = "all"
    TIME = "time"
    RENDER = "render"
    MEMORY = "memory"
    OBJECTS = "objects"


class GetPerformanceMetricsInput(BaseModel):
    """Input model for godot_get_performance_metrics."""

    category: MetricCategory = Field(
        default=MetricCategory.ALL,
        description="Category of metrics to retrieve: 'all', 'time' (FPS, process/physics durations), 'render' (draw calls, objects, primitives, VRAM), 'memory' (RAM usage, peak), or 'objects' (node/resource counts, orphan nodes).",
    )
    include_custom_monitors: bool = Field(
        default=True,
        description="Whether to include user-registered custom performance monitors.",
    )
