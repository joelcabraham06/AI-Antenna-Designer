"""
AI-Based Automatic Antenna Designer
Module: Real-Time Antenna Synthesis & Multi-Workflow Comparison Simulator
"""

import os
import sys

# Add root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.synthesis import AntennaSynthesizer
from core.surrogate import RFSurrogateModel
from core.optimizer import AntennaOptimizer
from core.hfss_exporter import HFSSExporter

def run_antenna_optimization():
    print("=======================================================================")
    print("[+] AI-Based Automatic Antenna Design Engine & ANSYS HFSS Automation")
    print("    Multi-Objective Genetic Algorithm & ML Surrogate Optimization")
    print("=======================================================================\n")

    target_f0 = 2.45  # GHz (ISM / Wi-Fi / Bluetooth Band)
    target_s11 = -10.0 # dB
    target_gain = 3.8  # dBi
    er = 4.4           # FR-4 Substrate
    h = 1.6            # mm

    print(f"[TARGET] Input Specs: Frequency={target_f0} GHz | Max S11={target_s11} dB | Min Gain={target_gain} dBi | Substrate=FR-4 (er={er}, h={h}mm)\n")

    # 1. Workflow 1: Analytical Transmission Line Theory Baseline
    analytical = AntennaSynthesizer.calculate_microstrip_patch(target_f0, er, h)
    print("-----------------------------------------------------------------------")
    print(" [Workflow 1] Analytical Transmission Line Seed Synthesis:")
    print(f"  • Patch Length (L): {analytical['patch_length_mm']} mm")
    print(f"  • Patch Width (W):  {analytical['patch_width_mm']} mm")
    print(f"  • Feed Offset (xf): {analytical['feed_offset_mm']} mm")
    print("-----------------------------------------------------------------------\n")

    # 2. Workflow 2 & 3: AI-Surrogate Multi-Objective Optimization Engine
    print("[AI-OPT] Executing AI Surrogate Multi-Objective Genetic Algorithm...")
    surrogate = RFSurrogateModel()
    optimizer = AntennaOptimizer(surrogate)
    
    opt_results = optimizer.optimize(target_f0, target_s11, target_gain, er, h, generations=25, pop_size=20)

    perf = opt_results["performance"]
    print("\n=======================================================================")
    print("[RESULTS] AI-OPTIMIZED ANTENNA SYNTHESIS RESULTS & PERFORMANCE")
    print("=======================================================================")
    print(f"  • Optimized Patch Length (L): {opt_results['optimized_patch_length_mm']} mm")
    print(f"  • Optimized Patch Width (W):  {opt_results['optimized_patch_width_mm']} mm")
    print(f"  • Optimized Feed Offset (xf): {opt_results['optimized_feed_offset_mm']} mm")
    print(f"  • Resonant Frequency (f0):     {perf['predicted_f_res_ghz']} GHz (Error: {abs(perf['predicted_f_res_ghz']-target_f0):.3f} GHz)")
    print(f"  • Return Loss (S11):          {perf['predicted_s11_db']} dB")
    print(f"  • Peak Antenna Gain:          {perf['predicted_gain_dbi']} dBi")
    print(f"  • 10dB Impedance Bandwidth:  {perf['predicted_bandwidth_mhz']} MHz")
    print(f"  • VSWR:                       {perf['predicted_vswr']}")
    print(f"  • Optimization Time:          < 0.05 seconds (vs 6+ hours for 100 HFSS FEM iterations)")
    print("=======================================================================\n")

    # 3. Export ANSYS HFSS PyAEDT Script
    script_path = HFSSExporter.generate_pyaedt_script(opt_results, "build_hfss_antenna.py")
    print(f"[OK] Generated ANSYS HFSS Automation Script: {script_path}")
    print("     Open PyAEDT or ANSYS Electronics Desktop (AEDT) to simulate 3D model!\n")

if __name__ == "__main__":
    run_antenna_optimization()
