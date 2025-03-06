# Read elevation raster
# ----------------------------
# print("catchment.py: Starting...")
from pysheds.grid import Grid
import argparse
import subprocess
import signal
import numpy as np


dirmap = (64, 128, 1, 2, 4, 8, 16, 32)

# Handle keyboard interrupts gracefully
def signal_handler(sig, frame):
    print("\ncatchment.py: Interrupted by user (Ctrl+C)")
    exit(1)

signal.signal(signal.SIGINT, signal_handler)


def calc_accumulation(d8_path, output_path):
    grid = Grid.from_raster(d8_path)
    fdir = grid.read_raster(d8_path)

    acc = grid.accumulation(fdir, dirmap=dirmap)
    acc_log10 = np.log10(acc + 1)  # Adding 1 to avoid log10(0)
    print(f"catchment.py: Saving accum raster {output_path}")
    grid.to_raster(acc_log10, output_path)


def calc_catchment(d8_path, x, y, output_path):
    # Read DEM
    # print(f"catchment.py: Reading D8 {d8_path}")
    grid = Grid.from_raster(d8_path)
    fdir = grid.read_raster(d8_path)

    # print("catchment.py: Computing flow directions...")
    # d8raster = grid.flowdir(dem, dirmap=dirmap, flats=0, pits=0, nodata_out=0)


    # catch = grid.catchment(x=1658, y=4076, fdir=fdir, dirmap=dirmap,
    catch = grid.catchment(x=x, y=y, fdir=fdir, dirmap=dirmap,
                       xytype='index')

    print(catch)
    print(f"catchment.py: Saving catchment raster {output_path}")
    grid.to_raster(catch, output_path, dtype=np.uint8)

    print("catchment.py: Done!")


# Extract river network
# ---------------------
# branches = grid.extract_river_network(fdir, acc > 50, dirmap=dirmap)


if __name__ == '__main__':
    # ARGS
    parser = argparse.ArgumentParser(description='Condition a DEM raster')
    parser.add_argument('input_d8_path', type=str, help='Path to D8 flow direction raster file')
    parser.add_argument('input_x', type=int, help='X pixel coordinate')
    parser.add_argument('input_y', type=int, help='Y pixel coordinate')
    parser.add_argument('output_catchment_path', type=str, help='Path for output catchment raster file')
    args = parser.parse_args()

    # CALS
    calc_catchment(args.input_d8_path, int(args.input_x), int(args.input_y), args.output_catchment_path)

# # print(args)


