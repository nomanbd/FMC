# Fast Monte Carlo Photon Dose Calculator (Linac)

This repository contains a **fast Monte Carlo (FMC)** prototype for photon radiotherapy dose calculation for linac platforms such as **Varian TrueBeam**, **Varian Halcyon**, and **Elekta Versa HD**.

> ⚠️ This is a research/educational prototype and **not** for clinical use.

## Features

- 3D voxelized patient/phantom geometry with HU-to-density conversion
- Linac presets with beam quality and source model parameters
- Fast photon transport with simplified interaction physics
- Pure-Python implementation with simplified transport kernels
- Dose scoring in Gy-like relative units (normalized by histories)
- Command-line interface for quick runs

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m fmc.cli --linac truebeam --histories 200000 --size 96 96 96 --spacing-mm 2.5
```

## Model summary

The simulation performs:

1. Source particle sampling (position, direction, energy) according to linac preset.
2. Free-path sampling using attenuation `mu(E, rho)` and voxel density.
3. Stochastic interaction selection (Compton-like vs photoelectric-like).
4. Local energy deposition with optional scattered continuation.
5. Dose accumulation in 3D grid.

The code is structured to allow replacing the simplified kernels with higher-fidelity cross sections, phase-space source modeling, and GPU acceleration.

## Clinical roadmap (recommended)

- Commission with measured PDD/profiles/output factors for each machine/energy.
- Add MLC and jaw transport with explicit head model.
- Add heterogeneity correction benchmarking (e.g., CIRS phantom).
- Validate against reference MC engines (EGSnrc/Geant4/MCsquare).
- Implement DICOM RT import/export workflow.

## License

MIT
