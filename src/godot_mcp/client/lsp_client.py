"""Godot GDScript Language Server Protocol (LSP) client communicating on port 6005 with static fallback."""

import asyncio
import json
import logging
import re
from pathlib import Path
from typing import Any

from godot_mcp.config import GodotConfig
from godot_mcp.models.common import EngineMode, StandardResult

logger = logging.getLogger(__name__)


class GodotLSPClient:
    """Client for Godot's GDScript Language Server (TCP port 6005) with static analysis fallback."""

    def __init__(
        self,
        config: GodotConfig | None = None,
        host: str = "127.0.0.1",
        port: int = 6005,
    ) -> None:
        self.config = config or GodotConfig.load()
        self.host = host
        self.port = port
        self._req_id = 1

    def _get_abs_path(self, file_path: str) -> Path:
        """Resolve a project path or res:// path to an absolute filesystem Path."""
        clean_path = file_path.removeprefix("res://")
        if self.config.project_path:
            return Path(self.config.project_path) / clean_path
        return Path(clean_path)

    def _file_uri(self, path: Path) -> str:
        """Convert a Path to a file URI."""
        return path.resolve().as_uri()

    async def _send_lsp_request(
        self, method: str, params: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Send an LSP request over TCP with standard Content-Length framing."""
        try:
            async with asyncio.timeout(2.0):
                reader, writer = await asyncio.open_connection(self.host, self.port)

                # Initialize handshake if needed
                init_payload = json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "initialize",
                        "params": {
                            "processId": None,
                            "rootUri": self._file_uri(
                                Path(self.config.project_path or ".")
                            ),
                            "capabilities": {},
                        },
                    }
                )
                init_msg = f"Content-Length: {len(init_payload)}\r\n\r\n{init_payload}".encode()
                writer.write(init_msg)
                await writer.drain()

                # Read init response
                await self._read_lsp_message(reader)

                # Send actual request
                self._req_id += 1
                req_payload = json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": self._req_id,
                        "method": method,
                        "params": params,
                    }
                )
                req_msg = (
                    f"Content-Length: {len(req_payload)}\r\n\r\n{req_payload}".encode()
                )
                writer.write(req_msg)
                await writer.drain()

                resp = await self._read_lsp_message(reader)
                writer.close()
                await writer.wait_closed()
                return resp
        except (OSError, TimeoutError, json.JSONDecodeError) as e:
            logger.debug(
                "LSP TCP connection to %s:%d failed (%s), using static analysis.",
                self.host,
                self.port,
                e,
            )
            return None

    async def _read_lsp_message(
        self, reader: asyncio.StreamReader
    ) -> dict[str, Any] | None:
        """Read a single LSP message with Content-Length header."""
        header_bytes = await reader.readuntil(b"\r\n\r\n")
        header_text = header_bytes.decode("utf-8", errors="replace")
        length = 0
        for line in header_text.split("\r\n"):
            if line.lower().startswith("content-length:"):
                length = int(line.split(":")[1].strip())
                break
        if length > 0:
            body_bytes = await reader.readexactly(length)
            return json.loads(body_bytes.decode("utf-8", errors="replace"))
        return None

    async def query(
        self,
        file_path: str,
        query_type: str = "symbols",
        line: int = 1,
        character: int = 1,
        symbol_name: str | None = None,
    ) -> StandardResult:
        """Execute an LSP query with live daemon connection or static fallback."""
        abs_path = self._get_abs_path(file_path)
        if not abs_path.exists():
            return StandardResult(
                success=False,
                message=f"GDScript file not found: '{file_path}'.",
                mode=EngineMode.HEADLESS_CLI,
                error_code="FILE_NOT_FOUND",
            )

        doc_uri = self._file_uri(abs_path)
        # Convert 1-indexed line/char to 0-indexed for LSP
        lsp_pos = {"line": max(0, line - 1), "character": max(0, character - 1)}

        # Try live LSP first
        if query_type == "symbols":
            resp = await self._send_lsp_request(
                "textDocument/documentSymbol", {"textDocument": {"uri": doc_uri}}
            )
            if resp and "result" in resp:
                symbols = resp["result"] or []
                if symbol_name:
                    symbols = [
                        s
                        for s in symbols
                        if symbol_name.lower() in s.get("name", "").lower()
                    ]
                return StandardResult(
                    success=True,
                    message=f"Found {len(symbols)} symbols in '{file_path}' (Live LSP).",
                    mode=EngineMode.LIVE_EDITOR,
                    data={
                        "file_path": file_path,
                        "query_type": query_type,
                        "symbols": symbols,
                    },
                )

        elif query_type == "definition":
            resp = await self._send_lsp_request(
                "textDocument/definition",
                {"textDocument": {"uri": doc_uri}, "position": lsp_pos},
            )
            if resp and "result" in resp:
                return StandardResult(
                    success=True,
                    message=f"Definition lookup succeeded for '{file_path}' at L{line}:C{character} (Live LSP).",
                    mode=EngineMode.LIVE_EDITOR,
                    data={
                        "file_path": file_path,
                        "query_type": query_type,
                        "definition": resp["result"],
                    },
                )

        elif query_type == "references":
            resp = await self._send_lsp_request(
                "textDocument/references",
                {
                    "textDocument": {"uri": doc_uri},
                    "position": lsp_pos,
                    "context": {"includeDeclaration": True},
                },
            )
            if resp and "result" in resp:
                return StandardResult(
                    success=True,
                    message=f"Found {len(resp['result'] or [])} references across project (Live LSP).",
                    mode=EngineMode.LIVE_EDITOR,
                    data={
                        "file_path": file_path,
                        "query_type": query_type,
                        "references": resp["result"],
                    },
                )

        elif query_type == "hover":
            resp = await self._send_lsp_request(
                "textDocument/hover",
                {"textDocument": {"uri": doc_uri}, "position": lsp_pos},
            )
            if resp and "result" in resp:
                return StandardResult(
                    success=True,
                    message=f"Hover inspection for '{file_path}' at L{line}:C{character} (Live LSP).",
                    mode=EngineMode.LIVE_EDITOR,
                    data={
                        "file_path": file_path,
                        "query_type": query_type,
                        "hover": resp["result"],
                    },
                )

        # Static analysis fallback
        return self._static_query(
            abs_path, file_path, query_type, line, character, symbol_name
        )

    def _static_query(
        self,
        abs_path: Path,
        file_path: str,
        query_type: str,
        line: int,
        character: int,
        symbol_name: str | None = None,
    ) -> StandardResult:
        """Perform static GDScript code analysis when LSP daemon is offline."""
        content = abs_path.read_text(encoding="utf-8", errors="replace")
        lines = content.splitlines()

        if query_type == "symbols":
            symbols = []
            for idx, l in enumerate(lines):
                s_strip = l.strip()
                match_func = re.match(r"^func\s+([a-zA-Z0-9_]+)\s*\((.*?)\)", s_strip)
                if match_func:
                    symbols.append(
                        {
                            "name": match_func.group(1),
                            "kind": "Function",
                            "line": idx + 1,
                            "signature": f"func {match_func.group(1)}({match_func.group(2)})",
                        }
                    )
                    continue
                match_var = re.match(
                    r"^(?:@onready\s+|@export\s+)?var\s+([a-zA-Z0-9_]+)", s_strip
                )
                if match_var:
                    symbols.append(
                        {
                            "name": match_var.group(1),
                            "kind": "Variable",
                            "line": idx + 1,
                            "signature": s_strip,
                        }
                    )
                    continue
                match_sig = re.match(r"^signal\s+([a-zA-Z0-9_]+)", s_strip)
                if match_sig:
                    symbols.append(
                        {
                            "name": match_sig.group(1),
                            "kind": "Signal",
                            "line": idx + 1,
                            "signature": s_strip,
                        }
                    )
                    continue
                match_const = re.match(r"^const\s+([a-zA-Z0-9_]+)", s_strip)
                if match_const:
                    symbols.append(
                        {
                            "name": match_const.group(1),
                            "kind": "Constant",
                            "line": idx + 1,
                            "signature": s_strip,
                        }
                    )
                    continue
                match_class = re.match(r"^class_name\s+([a-zA-Z0-9_]+)", s_strip)
                if match_class:
                    symbols.append(
                        {
                            "name": match_class.group(1),
                            "kind": "Class",
                            "line": idx + 1,
                            "signature": s_strip,
                        }
                    )

            if symbol_name:
                symbols = [
                    s for s in symbols if symbol_name.lower() in str(s["name"]).lower()
                ]

            return StandardResult(
                success=True,
                message=f"Found {len(symbols)} symbols in '{file_path}' (Static Analysis).",
                mode=EngineMode.HEADLESS_CLI,
                data={
                    "file_path": file_path,
                    "query_type": query_type,
                    "symbols": symbols,
                },
                actionable_hint="Launch Godot Editor on port 6005 for full live semantic LSP analysis.",
            )

        # Extract word at position
        target_line = lines[line - 1] if 0 <= line - 1 < len(lines) else ""
        word = self._extract_word(target_line, character - 1)

        if not word:
            return StandardResult(
                success=False,
                message=f"No valid symbol found at L{line}:C{character} in '{file_path}'.",
                mode=EngineMode.HEADLESS_CLI,
                error_code="SYMBOL_NOT_FOUND",
            )

        if query_type == "definition":
            # Search for declaration in current file and project files
            decl = self._find_definition_in_file(abs_path, word)
            if not decl and self.config.project_path:
                proj_root = Path(self.config.project_path)
                for gd_file in proj_root.rglob("*.gd"):
                    if gd_file == abs_path:
                        continue
                    decl = self._find_definition_in_file(gd_file, word)
                    if decl:
                        break

            if decl:
                return StandardResult(
                    success=True,
                    message=f"Found definition for '{word}' at {decl['file']}:{decl['line']}.",
                    mode=EngineMode.HEADLESS_CLI,
                    data={
                        "file_path": file_path,
                        "query_type": query_type,
                        "symbol": word,
                        "definition": decl,
                    },
                )
            return StandardResult(
                success=False,
                message=f"Could not find declaration for symbol '{word}'.",
                mode=EngineMode.HEADLESS_CLI,
                error_code="DEFINITION_NOT_FOUND",
            )

        elif query_type == "references":
            refs = []
            proj_root = (
                Path(self.config.project_path)
                if self.config.project_path
                else abs_path.parent
            )
            for gd_file in proj_root.rglob("*.gd"):
                try:
                    f_content = gd_file.read_text(encoding="utf-8", errors="replace")
                    for i, l in enumerate(f_content.splitlines()):
                        if re.search(r"\b" + re.escape(word) + r"\b", l):
                            rel = (
                                str(gd_file.relative_to(proj_root))
                                if self.config.project_path
                                else gd_file.name
                            )
                            refs.append(
                                {
                                    "file": f"res://{rel}",
                                    "line": i + 1,
                                    "line_content": l.strip(),
                                }
                            )
                except OSError:
                    continue

            return StandardResult(
                success=True,
                message=f"Found {len(refs)} references to '{word}' across project.",
                mode=EngineMode.HEADLESS_CLI,
                data={
                    "file_path": file_path,
                    "query_type": query_type,
                    "symbol": word,
                    "references": refs,
                },
            )

        elif query_type == "hover":
            # Gather doc comments before symbol
            doc_lines = []
            decl_line = target_line
            curr_idx = line - 2
            while curr_idx >= 0:
                prev_line = lines[curr_idx].strip()
                if prev_line.startswith("#"):
                    doc_lines.insert(0, prev_line.lstrip("#").strip())
                    curr_idx -= 1
                else:
                    break

            hover_info = {
                "symbol": word,
                "signature": decl_line.strip(),
                "docstring": "\n".join(doc_lines) if doc_lines else None,
            }
            return StandardResult(
                success=True,
                message=f"Hover info for symbol '{word}'.",
                mode=EngineMode.HEADLESS_CLI,
                data={
                    "file_path": file_path,
                    "query_type": query_type,
                    "hover": hover_info,
                },
            )

        return StandardResult(
            success=False,
            message=f"Unknown query_type: '{query_type}'.",
            mode=EngineMode.HEADLESS_CLI,
            error_code="INVALID_ARGUMENTS",
        )

    def _extract_word(self, line: str, col: int) -> str:
        """Extract the identifier under column offset."""
        if col < 0 or col >= len(line):
            col = max(0, min(col, len(line) - 1))
        # Find word boundaries
        start = col
        while start > 0 and (line[start - 1].isalnum() or line[start - 1] == "_"):
            start -= 1
        end = col
        while end < len(line) and (line[end].isalnum() or line[end] == "_"):
            end += 1
        return line[start:end].strip()

    def _find_definition_in_file(
        self, file_path: Path, symbol: str
    ) -> dict[str, Any] | None:
        """Search a GDScript file for definition of symbol."""
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            for idx, l in enumerate(content.splitlines()):
                patterns = [
                    rf"^func\s+{re.escape(symbol)}\b",
                    rf"^(?:@onready\s+|@export\s+)?var\s+{re.escape(symbol)}\b",
                    rf"^const\s+{re.escape(symbol)}\b",
                    rf"^signal\s+{re.escape(symbol)}\b",
                    rf"^class_name\s+{re.escape(symbol)}\b",
                ]
                for p in patterns:
                    if re.search(p, l.strip()):
                        rel = (
                            str(file_path.relative_to(Path(self.config.project_path)))
                            if self.config.project_path
                            else file_path.name
                        )
                        return {
                            "file": f"res://{rel}",
                            "line": idx + 1,
                            "line_content": l.strip(),
                        }
        except OSError:
            pass
        return None

    async def rename(
        self,
        file_path: str,
        line: int,
        character: int,
        new_name: str,
    ) -> StandardResult:
        """Execute a cross-file semantic rename."""
        abs_path = self._get_abs_path(file_path)
        if not abs_path.exists():
            return StandardResult(
                success=False,
                message=f"GDScript file not found: '{file_path}'.",
                mode=EngineMode.HEADLESS_CLI,
                error_code="FILE_NOT_FOUND",
            )

        # Check word at position
        content = abs_path.read_text(encoding="utf-8", errors="replace")
        lines = content.splitlines()
        target_line = lines[line - 1] if 0 <= line - 1 < len(lines) else ""
        old_name = self._extract_word(target_line, character - 1)

        if not old_name:
            return StandardResult(
                success=False,
                message=f"No identifier found at L{line}:C{character} in '{file_path}'.",
                mode=EngineMode.HEADLESS_CLI,
                error_code="SYMBOL_NOT_FOUND",
            )

        if old_name == new_name:
            return StandardResult(
                success=True,
                message=f"Symbol is already named '{new_name}'. No changes needed.",
                mode=EngineMode.HEADLESS_CLI,
                data={"old_name": old_name, "new_name": new_name, "modified_files": []},
            )

        proj_root = (
            Path(self.config.project_path)
            if self.config.project_path
            else abs_path.parent
        )
        modified_files = []
        pattern = re.compile(rf"\b{re.escape(old_name)}\b")

        for gd_file in proj_root.rglob("*.gd"):
            try:
                f_text = gd_file.read_text(encoding="utf-8", errors="replace")
                if pattern.search(f_text):
                    new_text = pattern.sub(new_name, f_text)
                    gd_file.write_text(new_text, encoding="utf-8")
                    rel = (
                        str(gd_file.relative_to(proj_root))
                        if self.config.project_path
                        else gd_file.name
                    )
                    modified_files.append(f"res://{rel}")
            except OSError:
                continue

        return StandardResult(
            success=True,
            message=f"Renamed symbol '{old_name}' -> '{new_name}' across {len(modified_files)} files.",
            mode=EngineMode.HEADLESS_CLI,
            data={
                "old_name": old_name,
                "new_name": new_name,
                "modified_files": modified_files,
            },
        )
