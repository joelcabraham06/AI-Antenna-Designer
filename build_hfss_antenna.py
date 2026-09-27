"""
ANSYS HFSS PyAEDT Automation Script
Generated automatically by AI-Antenna-Designer
Target Frequency: 2.45 GHz | Expected S11: -19.08 dB
"""

try:
    from pyaedt import Hfss
except ImportError:
    print("PyAEDT not detected locally. Script ready for ANSYS AEDT execution.")

def build_antenna():
    print("Connecting to ANSYS Electronics Desktop (AEDT)...")
    hfss = Hfss(specified_version="2026.1", non_graphical=False, new_desktop_session=True)
    
    # 1. Set Project Variables
    hfss["patch_L"] = "29.897mm"
    hfss["patch_W"] = "39.199mm"
    hfss["feed_offset"] = "2.339mm"
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
    setup = hfss.create_setup(name="Setup_2.45GHz")
    setup.props["Frequency"] = "2.45GHz"
    setup.props["MaximumPasses"] = 12
    
    sweep = setup.create_frequency_sweep(name="Sweep_1to5GHz", start_frequency="1GHz", stop_frequency="5GHz", num_of_freq_points=401)

    print("Saving AEDT Project...")
    hfss.save_project("AI_Optimized_Microstrip_2.45GHz.aedt")
    print("ANSYS HFSS Model Construction Complete!")

if __name__ == "__main__":
    build_antenna()
