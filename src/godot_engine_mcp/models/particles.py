"""Pydantic models for Godot VFX Particle systems (GPUParticles3D/2D, CPUParticles, ParticleProcessMaterial)."""

from enum import Enum

from pydantic import BaseModel, Field


class ParticleEngineType(str, Enum):
    """Particle node system types."""

    GPU_3D = "gpu_3d"
    CPU_3D = "cpu_3d"
    GPU_2D = "gpu_2d"
    CPU_2D = "cpu_2d"


class ParticleEmissionShape(str, Enum):
    """Emission spawn shape volumes."""

    POINT = "point"
    SPHERE = "sphere"
    BOX = "box"
    RING = "ring"


class ConfigureParticlesInput(BaseModel):
    """Input model for godot_configure_particles."""

    node_path: str | None = Field(
        default=None,
        description="Path to an existing particle node in the active scene to configure.",
    )
    parent_path: str | None = Field(
        default=None,
        description="Parent node path if creating a new particle system node.",
    )
    node_name: str | None = Field(
        default=None,
        description="Name for the newly created particle node (e.g. 'FireVFX', 'Sparks').",
    )
    save_path: str | None = Field(
        default=None,
        description="Optional file path to save the configured ParticleProcessMaterial as a .tres resource.",
    )
    particle_type: ParticleEngineType = Field(
        default=ParticleEngineType.GPU_3D,
        description="Particle system engine type ('gpu_3d', 'cpu_3d', 'gpu_2d', 'cpu_2d').",
    )
    amount: int = Field(
        default=64,
        description="Total simultaneous active particle count.",
    )
    lifetime: float = Field(
        default=1.0,
        description="Lifetime of each particle in seconds.",
    )
    explosiveness: float = Field(
        default=0.0,
        description="Emission explosiveness ratio (0.0 = continuous stream, 1.0 = single burst).",
    )
    emission_shape: ParticleEmissionShape = Field(
        default=ParticleEmissionShape.POINT,
        description="Emission shape ('point', 'sphere', 'box', 'ring').",
    )
    emission_sphere_radius: float | None = Field(
        default=None,
        description="Radius in meters when emission_shape is 'sphere' or 'ring'.",
    )
    emission_box_extents: tuple[float, float, float] | None = Field(
        default=None,
        description="Half-extents (x, y, z) in meters when emission_shape is 'box'.",
    )
    direction: tuple[float, float, float] = Field(
        default=(0.0, 1.0, 0.0),
        description="Unit emission direction vector (x, y, z).",
    )
    spread: float = Field(
        default=45.0,
        description="Emission spread angle in degrees.",
    )
    initial_velocity_min: float = Field(
        default=2.0,
        description="Minimum initial velocity in m/s.",
    )
    initial_velocity_max: float = Field(
        default=5.0,
        description="Maximum initial velocity in m/s.",
    )
    gravity: tuple[float, float, float] = Field(
        default=(0.0, -9.8, 0.0),
        description="Gravity acceleration vector (x, y, z) in m/s^2.",
    )
    color_gradient: list[str] | None = Field(
        default=None,
        description="List of Hex RGBA color stops defining the particle lifetime color ramp (e.g. ['#ffcc00ff', '#ff3300aa', '#22222200']).",
    )
    scale_min: float = Field(
        default=1.0,
        description="Minimum particle scale factor.",
    )
    scale_max: float = Field(
        default=1.0,
        description="Maximum particle scale factor.",
    )
    emitting: bool = Field(
        default=True,
        description="Whether particle emission is actively running.",
    )
