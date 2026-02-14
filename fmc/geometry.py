from __future__ import annotations

from dataclasses import dataclass


def hu_to_density_scalar(hu: float) -> float:
    if hu < -100:
        rho = max(0.1, min(1.0, 1.0 + hu / 1000.0))
    elif hu <= 200:
        rho = 1.0 + hu / 1200.0
    else:
        rho = 1.15 + (hu - 200) / 1800.0
    return max(0.1, min(2.5, rho))


@dataclass(slots=True)
class Volume3D:
    shape: tuple[int, int, int]
    data: list[float]

    @classmethod
    def filled(cls, shape: tuple[int, int, int], value: float = 0.0) -> "Volume3D":
        sx, sy, sz = shape
        return cls(shape=shape, data=[value] * (sx * sy * sz))

    def flat_index(self, i: int, j: int, k: int) -> int:
        _, sy, sz = self.shape
        return i * sy * sz + j * sz + k

    def get(self, i: int, j: int, k: int) -> float:
        return self.data[self.flat_index(i, j, k)]

    def set(self, i: int, j: int, k: int, value: float) -> None:
        self.data[self.flat_index(i, j, k)] = value

    def add(self, i: int, j: int, k: int, value: float) -> None:
        idx = self.flat_index(i, j, k)
        self.data[idx] += value

    def max(self) -> float:
        return max(self.data) if self.data else 0.0

    def mean(self) -> float:
        return sum(self.data) / len(self.data) if self.data else 0.0


@dataclass(slots=True)
class VoxelGrid:
    density_gcc: Volume3D
    spacing_mm: tuple[float, float, float]
    origin_mm: tuple[float, float, float] = (0.0, 0.0, 0.0)

    @classmethod
    def from_hu(
        cls,
        hu_volume: Volume3D,
        spacing_mm: tuple[float, float, float],
        origin_mm: tuple[float, float, float] = (0.0, 0.0, 0.0),
    ) -> "VoxelGrid":
        density = Volume3D.filled(hu_volume.shape, 0.0)
        sx, sy, sz = hu_volume.shape
        for i in range(sx):
            for j in range(sy):
                for k in range(sz):
                    density.set(i, j, k, hu_to_density_scalar(hu_volume.get(i, j, k)))
        return cls(density_gcc=density, spacing_mm=spacing_mm, origin_mm=origin_mm)

    @property
    def shape(self) -> tuple[int, int, int]:
        return self.density_gcc.shape

    @property
    def extent_mm(self) -> tuple[float, float, float]:
        sx, sy, sz = self.shape
        dx, dy, dz = self.spacing_mm
        return sx * dx, sy * dy, sz * dz

    def world_to_index(self, position_mm: tuple[float, float, float]) -> tuple[int, int, int]:
        ox, oy, oz = self.origin_mm
        dx, dy, dz = self.spacing_mm
        x, y, z = position_mm
        return int((x - ox) // dx), int((y - oy) // dy), int((z - oz) // dz)

    def in_bounds(self, ijk: tuple[int, int, int]) -> bool:
        i, j, k = ijk
        sx, sy, sz = self.shape
        return 0 <= i < sx and 0 <= j < sy and 0 <= k < sz
