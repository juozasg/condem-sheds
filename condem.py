# Read elevation raster
# ----------------------------
print("condem.py: Starting...")
from pysheds.grid import Grid
import argparse
import subprocess
import signal
from d8 import calc_d8
from catchment import calc_catchment, calc_accumulation


# Handle keyboard interrupts gracefully
def signal_handler(sig, frame):
    print("\ncondem.py: Interrupted by user (Ctrl+C)")
    exit(1)

signal.signal(signal.SIGINT, signal_handler)


def condition_dem(dem_path, condem_path, eps, max_iter):
    # Read DEM
    print(f"condem.py: Reading DEM {dem_path}")
    grid = Grid.from_raster(dem_path)
    dem = grid.read_raster(dem_path)

    # Condition DEM
    # ----------------------
    # Fill pits in DEM
    print("condem.py: Filling pits...")
    pit_filled_dem = grid.fill_pits(dem)

    # Fill depressions in DEM
    print("condem.py: Filling depressions...")
    flooded_dem = grid.fill_depressions(pit_filled_dem)

    # Resolve flats in DEM
    print("condem.py: Resolving flats...")
    inflated_dem = grid.resolve_flats(flooded_dem, eps=eps, max_iter=max_iter)
    Grid.resolve_flats

    # Save the condition DEM
    print(f"condem.py: Saving conditioned DEM {condem_path}")
    grid.to_raster(inflated_dem, condem_path)

    # Run gdalinfo -stats on the output DEM (last 10 lines)
    print("condem.py: gdalinfo -stats")
    print("--------------------------------")
    print(subprocess.getoutput(f"gdalinfo -stats {condem_path} | tail -n 10"))

    print("condem.py: Done!")



# LEZDOIT
condition_dem('data/source-full.tif', 'data/condem-full.tif', eps=1e-11, max_iter=100000)
calc_d8('data/condem-full.tif', 'data/d8-full.tif')
calc_accumulation('data/d8-full.tif', f'data/accum-full.tif')



# xi = 939
# yi = 3489
# calc_catchment('data/d8-full.tif', xi, yi, f'data/catchment-full-{xi}-{yi}.tif')

