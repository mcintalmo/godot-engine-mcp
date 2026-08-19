"""Common models, enums, and response formatting for Godot MCP."""

from enum import Enum
from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ResponseFormat(str, Enum):
    """Output format for tool responses."""

    MARKDOWN = "markdown"
    JSON = "json"


class EngineMode(str, Enum):
    """Current connection or execution mode with Godot."""

    LIVE_EDITOR = "live_editor"
    HEADLESS_CLI = "headless_cli"
    DISCONNECTED = "disconnected"


class BaseInputModel(BaseModel):
    """Base input model configuration."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )


class PaginationParams(BaseInputModel):
    """Pagination query parameters."""

    limit: int = Field(
        default=50, ge=1, le=500, description="Maximum number of items to return"
    )
    offset: int = Field(default=0, ge=0, description="Number of items to skip")


class PaginatedResponse[T](BaseModel):
    """Generic paginated response structure."""

    items: list[T]
    total_count: int
    offset: int
    limit: int
    has_more: bool
    next_offset: int | None = None


class StandardResult(BaseModel):
    """Standard operation execution result."""

    success: bool
    message: str
    mode: EngineMode
    data: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    error_code: str | None = None
    actionable_hint: str | None = None
