from __future__ import annotations

import math
import random


def attenuation_coeff_cm_inv(energy_mev: float, density_gcc: float) -> float:
    mu_mass = 0.018 + 0.06 / math.sqrt(max(energy_mev, 0.05))
    return mu_mass * density_gcc


def interaction_split(energy_mev: float) -> tuple[float, float]:
    p_photo = max(0.03, min(0.75, 0.35 / max(energy_mev, 0.1)))
    return p_photo, 1.0 - p_photo


def sample_scatter_direction(old_dir: tuple[float, float, float]) -> tuple[float, float, float]:
    cos_theta = random.uniform(0.6, 1.0)
    phi = random.uniform(0.0, 2.0 * math.pi)
    sin_theta = math.sqrt(max(0.0, 1.0 - cos_theta * cos_theta))
    sx = sin_theta * math.cos(phi)
    sy = sin_theta * math.sin(phi)
    sz = cos_theta

    ox, oy, oz = old_dir
    mx = 0.7 * ox + 0.3 * sx
    my = 0.7 * oy + 0.3 * sy
    mz = 0.7 * oz + 0.3 * sz
    norm = math.sqrt(mx * mx + my * my + mz * mz) or 1.0
    return mx / norm, my / norm, mz / norm
