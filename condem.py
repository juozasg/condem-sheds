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


# Loop through multiple variations of eps and max_iter values
# eps_values = [1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-11]
# max_iter_values = [10, 100, 1000, 10000, 100000]

# for eps in eps_values:
#     for max_iter in max_iter_values:
#         condem_path = f"data/condem-params/condem-ocpp-eps{eps}-iter{max_iter}.tif"
#         d8_path = f"data/condem-params/d8-ocpp-eps{eps}-iter{max_iter}.tif"
#         catchment_path = f"data/condem-params/catchment-ocpp-352-627-eps{eps}-iter{max_iter}.tif"
#         accum_path = f"data/condem-params/accum-ocpp-eps{eps}-iter{max_iter}.tif"
#         # condition_dem('data/source-ocpp.tif', condem_path, eps=eps, max_iter=max_iter)
#         # calc_d8(condem_path, d8_path)
#         # calc_catchment(d8_path, 352, 627, catchment_path)
#         calc_accumulation(d8_path, accum_path)



# condition_dem('data/source-full.tif', 'data/condem-full.tif', eps=1e-11, max_iter=100000)
# calc_d8('data/condem-full.tif', 'data/d8-full.tif')
xi = 939
yi = 3489
calc_catchment('data/d8-full.tif', xi, yi, f'data/catchment-full-{xi}-{yi}.tif')
# calc_accumulation('data/d8-full.tif', f'data/accum-full.tif')

# # ARGS
# parser = argparse.ArgumentParser(description='Condition a DEM raster')
# parser.add_argument('input_dem_path', type=str, help='Path to input DEM raster file')
# parser.add_argument('output_dem_path', type=str, help='Path for output hydrologically-conditioned raster file')
# args = parser.parse_args()

# print(args)

# condition_dem(args.input_dem_path, args.output_dem_path)

