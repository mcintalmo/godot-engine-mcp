"""Unit and headless tests for Godot Phase 30 tools (GPU Compute Shaders & RenderingDevice Pipelines)."""

import pytest

from godot_engine_mcp.client.headless_cli import HeadlessCLIClient
from godot_engine_mcp.config import GodotConfig
from godot_engine_mcp.models.rendering_device import (
    BufferBinding,
    DispatchComputeShaderInput,
    InspectRenderingDeviceInput,
)
from godot_engine_mcp.tools.rendering_device_tools import (
    handle_dispatch_compute_shader,
    handle_inspect_rendering_device,
)
from tests.test_tools import MockGodotClient


@pytest.mark.asyncio
async def test_phase30_tools_mock() -> None:
    """Test Phase 30 tools with MockGodotClient."""
    client = MockGodotClient()

    # 1. Dispatch Compute Shader
    compute_src = """
    #version 450
    layout(local_size_x = 64, local_size_y = 1, local_size_z = 1) in;
    layout(set = 0, binding = 0, std430) buffer MyBuffer {
        float data[];
    } my_buffer;
    void main() {
        uint idx = gl_GlobalInvocationID.x;
        my_buffer.data[idx] *= 2.0;
    }
    """
    cs_res = await handle_dispatch_compute_shader(
        client,
        DispatchComputeShaderInput(
            shader_code=compute_src,
            input_buffers=[
                BufferBinding(binding=0, data=[1.0, 2.0, 3.0, 4.0, 5.0]),
            ],
            workgroup_size=[1, 1, 1],
            output_binding=0,
            output_element_count=5,
        ),
    )
    assert "Dispatched Compute Shader" in cs_res
    assert "Workgroup Size" in cs_res
    assert "Buffer Output" in cs_res

    # 2. Inspect RenderingDevice
    rd_res = await handle_inspect_rendering_device(
        client,
        InspectRenderingDeviceInput(extended_info=True),
    )
    assert "RenderingDevice Hardware Telemetry" in rd_res
    assert "Apple M-Series GPU" in rd_res
    assert "Max Workgroup Size" in rd_res


@pytest.mark.asyncio
async def test_phase30_headless_client(tmp_path: pytest.TempPathFactory) -> None:
    """Test Phase 30 tools with HeadlessCLIClient."""
    cfg = GodotConfig(project_path=str(tmp_path))
    client = HeadlessCLIClient(cfg)

    # 1. Dispatch Compute Shader headlessly
    cs_res = await handle_dispatch_compute_shader(
        client,
        DispatchComputeShaderInput(
            shader_code="#version 450\nvoid main() {}",
            workgroup_size=[2, 2, 1],
            output_element_count=4,
        ),
    )
    assert "Dispatched Compute Shader" in cs_res

    # 2. Inspect RenderingDevice headlessly
    rd_res = await handle_inspect_rendering_device(
        client,
        InspectRenderingDeviceInput(),
    )
    assert "RenderingDevice Hardware Telemetry" in rd_res
    assert "Headless Virtual GPU" in rd_res
