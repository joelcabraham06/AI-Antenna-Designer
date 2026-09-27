"""
Automated Unittest Test Suite for AI-Antenna-Designer
"""

import unittest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.synthesis import AntennaSynthesizer
from core.surrogate import RFSurrogateModel
from core.optimizer import AntennaOptimizer
from core.hfss_exporter import HFSSExporter

class TestAIAntennaDesigner(unittest.TestCase):
    def setUp(self):
        self.surrogate = RFSurrogateModel()
        self.optimizer = AntennaOptimizer(self.surrogate)

    def test_transmission_line_synthesis(self):
        synth = AntennaSynthesizer.calculate_microstrip_patch(2.45, 4.4, 1.6)
        self.assertGreater(synth["patch_length_mm"], 20.0)
        self.assertGreater(synth["patch_width_mm"], 25.0)

    def test_surrogate_prediction(self):
        pred = self.surrogate.predict(28.2, 37.0, 4.1, 4.4, 1.6)
        self.assertIn("predicted_f_res_ghz", pred)
        self.assertLess(pred["predicted_s11_db"], -10.0)
        self.assertGreater(pred["predicted_gain_dbi"], 3.0)

    def test_genetic_algorithm_optimization(self):
        res = self.optimizer.optimize(2.45, -10.0, 3.5, 4.4, 1.6, generations=10, pop_size=10)
        self.assertIn("optimized_patch_length_mm", res)
        self.assertLess(res["performance"]["predicted_s11_db"], -10.0)

    def test_pyaedt_script_generation(self):
        dummy_res = {
            "target_f0_ghz": 2.45,
            "optimized_patch_length_mm": 28.2,
            "optimized_patch_width_mm": 37.0,
            "optimized_feed_offset_mm": 4.1,
            "performance": {"predicted_s11_db": -25.0}
        }
        out_file = HFSSExporter.generate_pyaedt_script(dummy_res, "test_pyaedt.py")
        self.assertTrue(os.path.exists(out_file))
        if os.path.exists(out_file):
            os.remove(out_file)

if __name__ == "__main__":
    unittest.main()
