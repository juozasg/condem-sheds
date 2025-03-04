# Read elevation raster
# ----------------------------
# print("d8.py: Starting...")
from pysheds.grid import Grid
import argparse
# import subprocess
import signal
import numpy as np


# Handle keyboard interrupts gracefully
def signal_handler(sig, frame):
    print("\ncondem.py: Interrupted by user (Ctrl+C)")
    exit(1)

signal.signal(signal.SIGINT, signal_handler)


def calc_d8(dem_path, output_path):
    # Read DEM
    # print(f"d8.py: Reading DEM {dem_path}")
    grid = Grid.from_raster(dem_path)
    dem = grid.read_raster(dem_path)

    dirmap = (64, 128, 1, 2, 4, 8, 16, 32)
    print("d8.py: Computing flow directions...")
    d8raster = grid.flowdir(dem, dirmap=dirmap, flats=-1, pits=-2, nodata_out=0) # NODATA = go west (this is what we're gonna do)
    # d8raster = grid.flowdir(dem, dirmap=dirmap, flats=16, pits=16, nodata_out=16) # NODATA = go west (this is what we're gonna do)

    print(d8raster)
    print(f"d8.py: Saving D8 raster {output_path}")
    grid.to_raster(d8raster, output_path, dtype=np.int16)

    print("d8.py: Done!")


# ARGS
# parser = argparse.ArgumentParser(description='Condition a DEM raster')
# parser.add_argument('input_dem_path', type=str, help='Path to input hydrologically-conditioned DEM raster file')
# parser.add_argument('output_d8_path', type=str, help='Path for output D8 flow direction raster file')
# args = parser.parse_args()

# print(args)

# calc_d8(args.input_dem_path, args.output_d8_path)

