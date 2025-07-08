#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script runs a particle injection simulation using the Prometheus framework.

It performs the following steps:
1.  Sets up the Python environment to locate the custom-compiled LeptonInjector
    and Prometheus libraries within the active Conda environment.
2.  Configures simulation parameters, including run number, event count,
    detector geometry, and particle injection settings.
3.  Initializes the Prometheus simulation object.
4.  Executes the simulation.
"""

import os
import sys
from ctypes import CDLL

def setup_pre_import_environment():
    """
    Modifies the system path and library path to ensure custom libraries are found.
    This function MUST be called BEFORE attempting to import prometheus or LeptonInjector.
    """
    print("--- Setting up pre-import environment ---")
    
    # Ensure the CONDA_PREFIX environment variable is set
    if "CONDA_PREFIX" not in os.environ:
        raise EnvironmentError(
            "CONDA_PREFIX is not set. Please run this script from an active Conda environment."
        )
        
    conda_prefix = os.environ["CONDA_PREFIX"]
    
    # --- Fix for 'cannot open shared object file' and 'not found' errors ---
    # Add the conda environment's lib directory to the library search path.
    # This is the most critical step and must happen before any C++-backed imports.
    lib_dir = os.path.join(conda_prefix, "lib")
    current_ld_path = os.environ.get("LD_LIBRARY_PATH", "")
    if lib_dir not in current_ld_path.split(os.pathsep):
        print(f"Adding to LD_LIBRARY_PATH: {lib_dir}")
        os.environ["LD_LIBRARY_PATH"] = f"{lib_dir}{os.pathsep}{current_ld_path}"
    
    # Add the environment's site-packages to the Python path.
    # This helps Python find the installed prometheus and LeptonInjector modules.
    pkgs_path = os.path.join(conda_prefix, "lib", "python3.11", "site-packages")
    if pkgs_path not in sys.path:
        sys.path.insert(0, pkgs_path)
        print(f"Added to sys.path: {pkgs_path}")

    # The following section manually loads a shared library.
    # This can sometimes resolve dynamic linking issues.
    try:
        lib_path = os.path.join(conda_prefix, "lib", "libpython3.11.so.1.0")
        if os.path.exists(lib_path):
            print(f"Attempting to force-load shared library: {lib_path}")
            CDLL(lib_path)
        else:
            print(f"Warning: Shared library not found at {lib_path}. Skipping force-load.")
    except Exception as e:
        print(f"Warning: Could not force-load library. This may be okay on your system. Error: {e}")

    print("--- Pre-import environment setup complete ---\n")


def main():
    """
    Main function to configure and run the Prometheus simulation.
    """
    # Set up all environment variables and paths *before* running the simulation.
    # This is the fix for the "cannot open shared object file" error.
    setup_pre_import_environment()

    # --- Import Modules ---
    # Now that the environment is set, we can safely import the modules.
    try:
        import numpy as np
        import prometheus
        from prometheus import config, Prometheus
    except ImportError as e:
        print(f"Fatal: Failed to import a required module: {e}")
        print("Please ensure Prometheus is correctly installed in your active Conda environment.")
        sys.exit(1)

    # --- Configure Simulation ---
    print("--- Configuring simulation ---")

    # Dynamically find the prometheus base directory from its installation path.
    prometheus_package_path = prometheus.__path__[0]
    prometheus_base = os.path.dirname(prometheus_package_path)
    print(f"Detected Prometheus base directory: {prometheus_base}")
    
    # --- Fix for 'EarthModelService' initialization error ---
    # The EarthModelService C++ library requires this environment variable to find
    # its data files (e.g., prem.dat).
    earth_params_path = os.path.join(prometheus_base, "resources", "earthparams")
    print(f"Setting EARTH_PARAMS environment variable to: {earth_params_path}")
    os.environ["EARTH_PARAMS"] = earth_params_path

    resource_dir = os.path.join(prometheus_base, "resources")
    output_dir = os.path.join(prometheus_base, "examples", "output")
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Set run parameters
    config['run']["run number"] = 925
    config['run']['nevents'] = 100
    config['run']["storage prefix"] = output_dir
    config["run"]["outfile"] = f"output/{config['run']['run number']}_photons.parquet"

    # Set detector geometry
    geofile = os.path.join(resource_dir, "geofiles", "demo_ice.geo")
    config["detector"]["geo file"] = geofile
    print(f"Using geometry file: {geofile}")

    # Set injection parameters
    injector = "LeptonInjector"
    config["injection"]["name"] = injector
    injection_config = config["injection"][injector]

    # --- FIX FOR 'failed to open PREM_mmc.dat' ---
    # The LeptonInjector C++ code does not use the ["simulation"]["earth model"] key.
    # Instead, it requires a full path to the model data file to be set in
    # the ['paths']['earth model location'] key.
    earth_model_file = os.path.join(resource_dir, 'earthparams', 'densities', 'PREM_south_pole.dat')
    injection_config['paths']['earth model location'] = earth_model_file
    print(f"Set LeptonInjector earth model location to: {earth_model_file}")


    # Inject only upgoing events
    degrees = np.pi / 180
    injection_config["simulation"]["min zenith"] = 0 * degrees
    injection_config["simulation"]["max zenith"] = 90 * degrees

    # Inject with E from 100 GeV to 1 PeV, sampled according to E^-1
    injection_config["simulation"]["minimal energy"] = 1e2
    injection_config["simulation"]["maximal energy"] = 1e6
    injection_config["simulation"]["gamma"] = 1

    # Specify numu CC events
    injection_config["simulation"]["final state 1"] = "MuMinus"
    injection_config["simulation"]["final state 2"] = "Hadrons"
    
    print("Final configuration set:")
    print("--- Configuration complete ---\n")

    # --- Run Simulation ---
    current_directory = os.getcwd()
    print(f"The current working directory is: {current_directory}")
    print("Initializing Prometheus...")

    p = Prometheus(config)
    
    print("Starting simulation...")
    p.sim()
    print("--- Simulation finished ---")


if __name__ == "__main__":
    main()

