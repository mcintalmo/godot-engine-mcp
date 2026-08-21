"""Unit and headless tests for Godot Phase 13 tools (Project Asset Audit, Orphan Cleanup & Texture Validation)."""

import pytest

from godot_mcp.client.headless_cli import HeadlessCLIClient
from godot_mcp.config import GodotConfig
from godot_mcp.models.asset_audit import (
    AuditAssetsInput,
    CleanOrphansInput,
    GetTextureInfoInput,
)
from godot_mcp.tools.asset_audit_tools import (
    handle_audit_assets,
    handle_clean_orphans,
    handle_get_texture_info,
)
from tests.test_tools import MockGodotClient


@pytest.mark.asyncio
async def test_phase13_tools_mock() -> None:
    """Test Phase 13 tools with MockGodotClient."""
    client = MockGodotClient()

    # 1. Audit assets
    audit_res = await handle_audit_assets(
        client,
        AuditAssetsInput(include_extensions=[".png", ".wav"]),
    )
    assert "Asset Audit Summary" in audit_res
    assert "Orphan Files" in audit_res
    assert "old_texture.png" in audit_res

    # 2. Clean orphans (dry run)
    dry_clean_res = await handle_clean_orphans(
        client,
        CleanOrphansInput(dry_run=True),
    )
    assert "Simulated Orphan Cleanup" in dry_clean_res
    assert "old_texture.png" in dry_clean_res

    # 3. Clean orphans (quarantine)
    quar_clean_res = await handle_clean_orphans(
        client,
        CleanOrphansInput(
            dry_run=False,
            quarantine_folder="res://.quarantine",
        ),
    )
    assert "Orphan Files Quarantined" in quar_clean_res
    assert "res://.quarantine" in quar_clean_res

    # 4. Get texture info
    tex_res = await handle_get_texture_info(
        client,
        GetTextureInfoInput(texture_path="res://textures/diffuse.png"),
    )
    assert "Texture Diagnostics" in tex_res
    assert "1024x1024" in tex_res
    assert "Format_RGBA8" in tex_res


@pytest.mark.asyncio
async def test_phase13_headless_client(tmp_path: pytest.TempPathFactory) -> None:
    """Test Phase 13 tools with HeadlessCLIClient."""
    cfg = GodotConfig(project_path=str(tmp_path))
    client = HeadlessCLIClient(cfg)

    # 1. Audit assets headlessly
    audit_res = await handle_audit_assets(client, AuditAssetsInput())
    assert "Asset Audit Summary" in audit_res

    # 2. Clean orphans headlessly
    clean_res = await handle_clean_orphans(client, CleanOrphansInput(dry_run=True))
    assert "Simulated Orphan Cleanup" in clean_res

    # 3. Get texture info headlessly
    tex_res = await handle_get_texture_info(
        client,
        GetTextureInfoInput(texture_path="res://icon.png"),
    )
    assert "Texture Diagnostics" in tex_res
    assert "512x512" in tex_res
