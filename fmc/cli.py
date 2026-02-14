from __future__ import annotations

import argparse

from .engine import FMCConfig, DoseEngine
from .geometry import Volume3D, VoxelGrid
from .linac import get_linac_preset


def build_water_phantom(size: tuple[int, int, int]) -> Volume3D:
    sx, sy, sz = size
    hu = Volume3D.filled(size, 0.0)
    cx, cy = sx // 2, sy // 2
    outer = min(sx, sy) * 0.45
    inner = min(sx, sy) * 0.15

    for i in range(sx):
        for j in range(sy):
            r = ((i - cx) ** 2 + (j - cy) ** 2) ** 0.5
            for k in range(sz):
                if r > outer:
                    hu.set(i, j, k, -700.0)
                elif r < inner:
                    hu.set(i, j, k, 400.0)
    return hu


def main() -> None:
    parser = argparse.ArgumentParser(description="Fast Monte Carlo photon dose prototype")
    parser.add_argument("--linac", default="truebeam", choices=["truebeam", "halcyon", "versahd"])
    parser.add_argument("--histories", type=int, default=20000)
    parser.add_argument("--size", type=int, nargs=3, default=(64, 64, 64))
    parser.add_argument("--spacing-mm", type=float, default=2.5)
    parser.add_argument("--field-size-mm", type=float, nargs=2, default=(120.0, 120.0))
    args = parser.parse_args()

    hu = build_water_phantom(tuple(args.size))
    grid = VoxelGrid.from_hu(hu, spacing_mm=(args.spacing_mm, args.spacing_mm, args.spacing_mm))
    linac = get_linac_preset(args.linac)
    config = FMCConfig(histories=args.histories, field_size_mm=tuple(args.field_size_mm))

    result = DoseEngine(grid=grid, linac=linac, config=config).run()

    print(f"Linac: {linac.name}")
    print(f"Histories: {result.histories}")
    print(f"Deposited energy (MeV): {result.deposited_energy_mev:.3f}")
    print(f"Max relative dose: {result.dose.max():.6f}")
    print(f"Mean relative dose: {result.dose.mean():.6f}")


if __name__ == "__main__":
    main()
