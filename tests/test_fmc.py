import unittest

from fmc.engine import FMCConfig, DoseEngine
from fmc.geometry import Volume3D, VoxelGrid, hu_to_density_scalar
from fmc.linac import get_linac_preset


class FMCTests(unittest.TestCase):
    def test_hu_density_bounds(self):
        values = [-1000, -700, 0, 300, 1200]
        rho = [hu_to_density_scalar(v) for v in values]
        self.assertTrue(all(v >= 0.1 for v in rho))
        self.assertTrue(all(v <= 2.5 for v in rho))
        self.assertEqual(rho[2], 1.0)

    def test_linac_lookup_alias(self):
        a = get_linac_preset("versa-hd")
        b = get_linac_preset("versahd")
        self.assertEqual(a.name, b.name)

    def test_engine_deposits_energy(self):
        hu = Volume3D.filled((24, 24, 24), 0.0)
        grid = VoxelGrid.from_hu(hu, spacing_mm=(3.0, 3.0, 3.0))
        cfg = FMCConfig(histories=2000, max_interactions=60)
        result = DoseEngine(grid, get_linac_preset("truebeam"), cfg, rng_seed=0).run()

        self.assertGreater(result.deposited_energy_mev, 0.0)
        self.assertGreater(result.dose.max(), 0.0)
        self.assertEqual(result.dose.shape, hu.shape)


if __name__ == "__main__":
    unittest.main()
