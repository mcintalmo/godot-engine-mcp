"""Pydantic models for Godot GDScript Language Server Protocol (LSP) operations."""

from enum import Enum

from pydantic import BaseModel, Field


class LSPQueryType(str, Enum):
    """Types of semantic LSP queries supported."""

    SYMBOLS = "symbols"
    DEFINITION = "definition"
    REFERENCES = "references"
    HOVER = "hover"


class LSPQueryInput(BaseModel):
    """Input model for godot_lsp_query."""

    file_path: str = Field(
        ...,
        description="Path to the GDScript file (e.g. 'res://scripts/player.gd' or 'scripts/player.gd').",
    )
    query_type: LSPQueryType = Field(
        default=LSPQueryType.SYMBOLS,
        description="Type of LSP query to perform: 'symbols' (list symbols), 'definition' (go to definition), 'references' (find all references), or 'hover' (docstring and type inspection).",
    )
    line: int = Field(
        default=1,
        description="1-indexed line number in the target GDScript file (for definition, references, and hover).",
    )
    character: int = Field(
        default=1,
        description="1-indexed character column offset in the target line.",
    )
    symbol_name: str | None = Field(
        default=None,
        description="Optional symbol name filter (for 'symbols' query).",
    )


class LSPRenameInput(BaseModel):
    """Input model for godot_lsp_rename."""

    file_path: str = Field(
        ...,
        description="Path to the GDScript file containing the symbol to rename.",
    )
    line: int = Field(
        default=1,
        description="1-indexed line number of the symbol to rename.",
    )
    character: int = Field(
        default=1,
        description="1-indexed character column offset of the symbol.",
    )
    new_name: str = Field(
        ...,
        description="New identifier name for the symbol.",
    )
