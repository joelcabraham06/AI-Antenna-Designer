"""
AI-Based Automatic Antenna Designer
Module: PyAEDT & ANSYS HFSS Automation Script Exporter
"""

import os

class HFSSExporter:
    @staticmethod
    def generate_pyaedt_script(opt_results, output_filename="build_hfss_antenna.py"):
        """
        Generates an executable PyAEDT Python script that opens ANSYS Electronics Desktop (AEDT),
        constructs 3D Microstrip Patch antenna geometry, assigns materials, sets up Lumped Port excitation,
        creates air radiation boundary, and runs HFSS FEM solution sweep.
        """
        l = opt_results["optimized_patch_length_mm"]
        w = opt_results["optimized_patch_width_mm"]
        xf = opt_results["optimized_feed_offset_mm"]
        f0 = opt_results["target_f0_ghz"]
        s11 = opt_results["performance"]["predicted_s11_db"]

        script_content = f'''"""
ANSYS HFSS PyAEDT Automation Script
Generated automatically by AI-Antenna-Designer
Target Frequency: {f0} GHz | Expected S11: {s11} dB
"""

try:
    from pyaedt import Hfss
except ImportError:
    print("PyAEDT not detected locally. Script ready for ANSYS AEDT execution.")

def build_antenna():
    print("Connecting to ANSYS Electronics Desktop (AEDT)...")
    hfss = Hfss(specified_version="2026.1", non_graphical=False, new_desktop_session=True)
    
    # 1. Set Project Variables
    hfss["patch_L"] = "{l}mm"
    hfss["patch_W"] = "{w}mm"
    hfss["feed_offset"] = "{xf}mm"
    hfss["sub_h"] = "1.6mm"
    hfss["sub_er"] = "4.4"

    print("Creating 3D Microstrip Patch Antenna Geometry...")
    # Substrate
    sub = hfss.modeler.create_box(["-patch_W", "-patch_L", "0mm"], ["2*patch_W", "2*patch_L", "sub_h"], name="Substrate", matname="FR4_epoxy")
    
    # Ground Plane
    gnd = hfss.modeler.create_rectangle("XY", ["-patch_W", "-patch_L", "0mm"], ["2*patch_W", "2*patch_L"], name="GroundPlane")
    
    # Patch Antenna
    patch = hfss.modeler.create_rectangle("XY", ["0mm", "0mm", "sub_h"], ["patch_W", "patch_L"], name="MicrostripPatch")
    
    # Port Excitation
    port = hfss.modeler.create_rectangle("YZ", ["0mm", "feed_offset", "0mm"], ["sub_h", "1.5mm"], name="LumpedPort")
    hfss.create_lumped_port_to_sheet(port.name, port_between_rectangles=True)

    # Air Radiation Box
    air = hfss.modeler.create_box(["-2*patch_W", "-2*patch_L", "-10mm"], ["4*patch_W", "4*patch_L", "40mm"], name="AirBox", matname="air")
    hfss.assign_radiation_boundary_to_faces([face.id for face in air.faces])

    # 2. Setup Solution Frequency & Sweep
    setup = hfss.create_setup(name="Setup_{f0}GHz")
    setup.props["Frequency"] = "{f0}GHz"
    setup.props["MaximumPasses"] = 12
    
    sweep = setup.create_frequency_sweep(name="Sweep_1to5GHz", start_frequency="1GHz", stop_frequency="5GHz", num_of_freq_points=401)

    print("Saving AEDT Project...")
    hfss.save_project("AI_Optimized_Microstrip_{f0}GHz.aedt")
    print("ANSYS HFSS Model Construction Complete!")

if __name__ == "__main__":
    build_antenna()
'''

        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(script_content)

        return output_filename
