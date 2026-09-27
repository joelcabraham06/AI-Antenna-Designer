"""
AI-Based Automatic Antenna Designer
Module: Analytical Transmission Line Theory Antenna Synthesizer
"""

import math

class AntennaSynthesizer:
    c = 3.0e8 # Speed of light in m/s

    @staticmethod
    def calculate_microstrip_patch(f0_ghz, er=4.4, h_mm=1.6):
        """
        Calculates initial analytical patch dimensions L, W, and feed location
        using Transmission Line Theory equations.
        """
        f0 = f0_ghz * 1.0e9
        h = h_mm * 1.0e-3

        # 1. Patch Width (W)
        w = (self_c := 3.0e8) / (2 * f0) * math.sqrt(2 / (er + 1))

        # 2. Effective Dielectric Constant (e_eff)
        e_eff = (er + 1) / 2.0 + ((er - 1) / 2.0) * (1.0 / math.sqrt(1 + 12 * (h / w)))

        # 3. Length Extension (delta_L)
        delta_l = 0.412 * h * ((e_eff + 0.3) * (w / h + 0.264)) / ((e_eff - 0.258) * (w / h + 0.8))

        # 4. Patch Length (L)
        l_eff = self_c / (2 * f0 * math.sqrt(e_eff))
        l = l_eff - 2 * delta_l

        # 5. Inset Feed Location (x_f) for 50 Ohm matching
        r_in = 90 * (er**2 / (er - 1)) * (w / l)**2 # Input impedance approx
        x_f = (l / math.pi) * math.asin(math.sqrt(50.0 / r_in)) if r_in > 50 else (l * 0.15)

        # Ground dimensions (L_g, W_g)
        l_g = l + 6 * h
        w_g = w + 6 * h

        return {
            "target_f0_ghz": f0_ghz,
            "substrate_er": er,
            "substrate_h_mm": h_mm,
            "patch_length_mm": round(l * 1000, 3),
            "patch_width_mm": round(w * 1000, 3),
            "feed_offset_mm": round(x_f * 1000, 3),
            "ground_length_mm": round(l_g * 1000, 3),
            "ground_width_mm": round(w_g * 1000, 3),
            "effective_er": round(e_eff, 4)
        }
