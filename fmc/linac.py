from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LinacPreset:
    name: str
    nominal_energy_mv: float
    mean_energy_mev: float
    spectral_sigma_mev: float
    source_to_axis_distance_mm: float
    focal_spot_sigma_mm: float
    head_scatter_factor: float


LINAC_PRESETS: dict[str, LinacPreset] = {
    "truebeam": LinacPreset(
        name="Varian TrueBeam 6X",
        nominal_energy_mv=6.0,
        mean_energy_mev=2.0,
        spectral_sigma_mev=0.55,
        source_to_axis_distance_mm=1000.0,
        focal_spot_sigma_mm=0.8,
        head_scatter_factor=1.02,
    ),
    "halcyon": LinacPreset(
        name="Varian Halcyon 6X-FFF",
        nominal_energy_mv=6.0,
        mean_energy_mev=1.8,
        spectral_sigma_mev=0.50,
        source_to_axis_distance_mm=1000.0,
        focal_spot_sigma_mm=1.0,
        head_scatter_factor=0.98,
    ),
    "versahd": LinacPreset(
        name="Elekta Versa HD 6MV",
        nominal_energy_mv=6.0,
        mean_energy_mev=2.1,
        spectral_sigma_mev=0.6,
        source_to_axis_distance_mm=1000.0,
        focal_spot_sigma_mm=0.9,
        head_scatter_factor=1.01,
    ),
}


def get_linac_preset(name: str) -> LinacPreset:
    key = name.lower().replace("-", "")
    if key not in LINAC_PRESETS:
        available = ", ".join(sorted(LINAC_PRESETS.keys()))
        raise ValueError(f"Unknown linac preset '{name}'. Available: {available}")
    return LINAC_PRESETS[key]
