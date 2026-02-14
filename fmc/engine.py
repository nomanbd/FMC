from __future__ import annotations

from dataclasses import dataclass
import math
import random

from .geometry import Volume3D, VoxelGrid
from .linac import LinacPreset
from .physics import attenuation_coeff_cm_inv, interaction_split, sample_scatter_direction


@dataclass(slots=True)
class FMCConfig:
    histories: int = 50_000
    batch_size: int = 1_000
    max_interactions: int = 60
    cutoff_energy_mev: float = 0.03
    field_size_mm: tuple[float, float] = (100.0, 100.0)


@dataclass(slots=True)
class SimulationResult:
    dose: Volume3D
    histories: int
    deposited_energy_mev: float


class DoseEngine:
    def __init__(self, grid: VoxelGrid, linac: LinacPreset, config: FMCConfig, rng_seed: int = 42) -> None:
        self.grid = grid
        self.linac = linac
        self.config = config
        random.seed(rng_seed)

    def run(self) -> SimulationResult:
        dose = Volume3D.filled(self.grid.shape, 0.0)
        deposited_total = 0.0

        for _ in range(self.config.histories):
            deposited_total += self._simulate_history(dose)

        norm = float(max(1, self.config.histories))
        dose.data = [v / norm for v in dose.data]
        return SimulationResult(dose=dose, histories=self.config.histories, deposited_energy_mev=deposited_total)

    def _simulate_history(self, dose: Volume3D) -> float:
        pos, direction, energy = self._sample_source_particle()
        deposited = 0.0

        for _ in range(self.config.max_interactions):
            ijk = self.grid.world_to_index(pos)
            if self.grid.in_bounds(ijk):
                rho = self.grid.density_gcc.get(*ijk)
            else:
                rho = 0.001
            mu_cm = attenuation_coeff_cm_inv(energy, rho)
            mu_mm = max(mu_cm / 10.0, 1e-6)

            xi = max(1e-6, random.random())
            step_mm = min(-math.log(xi) / mu_mm, 20.0)
            px, py, pz = pos
            dx, dy, dz = direction
            pos = (px + dx * step_mm, py + dy * step_mm, pz + dz * step_mm)

            ijk_int = self.grid.world_to_index(pos)
            if not self.grid.in_bounds(ijk_int):
                continue

            p_photo, _ = interaction_split(energy)
            is_photo = random.random() < p_photo
            e_dep = energy if is_photo else 0.12 * energy
            dose.add(*ijk_int, e_dep)
            deposited += e_dep

            if is_photo:
                break

            energy *= random.uniform(0.55, 0.9)
            direction = sample_scatter_direction(direction)
            if energy < self.config.cutoff_energy_mev:
                break

        return deposited

    def _sample_source_particle(self) -> tuple[tuple[float, float, float], tuple[float, float, float], float]:
        sx, sy, _ = self.grid.extent_mm
        x0 = sx * 0.5
        y0 = sy * 0.5
        z_src = -min(self.linac.source_to_axis_distance_mm, 300.0)

        fsx, fsy = self.config.field_size_mm
        fsx = min(fsx, sx * 0.9)
        fsy = min(fsy, sy * 0.9)
        tx = random.uniform(x0 - fsx / 2.0, x0 + fsx / 2.0)
        ty = random.uniform(y0 - fsy / 2.0, y0 + fsy / 2.0)
        tz = 0.0

        spot = self.linac.focal_spot_sigma_mm
        src = (
            random.gauss(x0, spot),
            random.gauss(y0, spot),
            z_src,
        )

        vx = tx - src[0]
        vy = ty - src[1]
        vz = tz - src[2]
        norm = math.sqrt(vx * vx + vy * vy + vz * vz) or 1.0
        direction = (vx / norm, vy / norm, vz / norm)

        energy = random.gauss(self.linac.mean_energy_mev, self.linac.spectral_sigma_mev)
        energy = min(6.0, max(0.05, energy)) * self.linac.head_scatter_factor
        return src, direction, energy
