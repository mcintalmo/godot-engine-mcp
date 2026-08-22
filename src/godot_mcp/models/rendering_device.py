"""Pydantic models for Godot GPU Compute Shaders & RenderingDevice Pipelines."""

from pydantic import BaseModel, Field


class BufferBinding(BaseModel):
    """Configuration for a compute shader buffer binding."""

    binding: int = Field(
        default=0,
        description="GLSL binding index.",
    )
    type: str = Field(
        default="storage_buffer",
        description="Buffer type: 'storage_buffer' or 'uniform_buffer'.",
    )
    data: list[float] | list[int] = Field(
        description="Initial float or integer payload for the buffer.",
    )


class DispatchComputeShaderInput(BaseModel):
    """Input model for godot_dispatch_compute_shader."""

    shader_code: str = Field(
        description="GLSL compute shader source code (e.g. '#version 450\\nlayout(local_size_x = 64) in;...').",
    )
    input_buffers: list[BufferBinding] = Field(
        default_factory=list,
        description="List of storage or uniform buffer bindings passed to the compute shader.",
    )
    workgroup_size: list[int] = Field(
        default=[1, 1, 1],
        description="Compute dispatch workgroup count [x, y, z].",
    )
    output_binding: int = Field(
        default=0,
        description="Binding index of the buffer to read back from GPU memory.",
    )
    output_element_count: int = Field(
        default=16,
        description="Number of float/int elements to read back from the output buffer.",
    )


class InspectRenderingDeviceInput(BaseModel):
    """Input model for godot_inspect_rendering_device."""

    extended_info: bool = Field(
        default=True,
        description="Whether to include detailed workgroup limits, memory limits, and supported formats.",
    )
