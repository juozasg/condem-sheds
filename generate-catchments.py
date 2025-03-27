import csv

# read csv file monitoring-d8-col-row.csv with cols siteId, col, row
# read csv file rivers-d8-col-row.csv with cols id, startCol, startRow, endCol, endRow

# Read monitoring-d8-col-row.csv
sites_with_raster_coords = []
with open('monitoring-d8-col-row.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader)  # Skip header row
    for row in reader:
        site_id, col, row = row
        sites_with_raster_coords.append([site_id, int(col), int(row)])


# Read rivers-d8-col-row.csv
rivers_with_raster_coords = []
with open('monitoring-d8-col-row.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader)  # Skip header row
    for row in reader:
        river_id, startCol, startRow, endCol, endRow = row
        rivers_with_raster_coords.append([river_id, int(startCol), int(startRow), int(endCol), int(endRow)])

print("generate-catchments.py: Starting...")
from catchment import calc_catchment

for site in sites_with_raster_coords:
    site_id, col, row = site
    name = f'site-{site_id}'
    print(f"generate-catchments.py: Generating catchment for site {site_id}")
    calc_catchment('data/condem-pass-2/output/d8.tif', col, row, f'generated-catchments/{name}.tif')

for river in rivers_with_raster_coords:
    river_id, startCol, startRow, endCol, endRow = river
    print(f"generate-catchments.py: Generating catchment for river {river_id}")
    name = f'river-star-{river_id}'
    calc_catchment('data/condem-pass-2/output/d8.tif', startCol, startRow, f'generated-catchments/{name}.tif')

    name = f'river-end-{river_id}'
    calc_catchment('data/condem-pass-2/output/d8.tif', endCol, endRow, f'generated-catchments/{name}.tif')