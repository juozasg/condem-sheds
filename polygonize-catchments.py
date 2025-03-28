import csv
import os


def polygonize_simplify_reproject(name):
    input_path = f'generated-catchments/{name}.tif'
    polygon_path = f'generated-catchments/geojson-temp/{name}.poly.geojson'
    simp_path = f'generated-catchments/geojson-temp/{name}.simp.geojson'
    reproj_path = f'generated-catchments/geojson/{name}.geojson'
    # if not os.path.isfile(polygon_path):
        # print(f"generate-catchments.py: Polygonizing, simplifying and reprojecting {input_path}")

    if not os.path.isfile(reproj_path):
        print("---POLUGONIZE---")
        os.system(f'gdal_polygonize.py {input_path} -8 -f geojson {polygon_path}')

        print("---SIMPLIFY---")
        os.system(f'qgis_process run native:simplifygeometries --distance_units=meters --area_units=m2 --ellipsoid=EPSG:7019 --INPUT={polygon_path} --METHOD=0 --TOLERANCE=10 --OUTPUT={simp_path}')

        print("---REPROJ---")
        os.system(f"qgis_process run native:reprojectlayer --distance_units=meters --area_units=m2 --ellipsoid=EPSG:7019 --INPUT={simp_path} --TARGET_CRS='EPSG:4326' --CONVERT_CURVED_GEOMETRIES=false --OPERATION='+proj=pipeline +step +inv +proj=utm +zone=16 +ellps=GRS80 +step +proj=push +v_3 +step +proj=cart +ellps=GRS80 +step +proj=helmert +x=-0.991 +y=1.9072 +z=0.5129 +rx=-0.0257899075194932 +ry=-0.0096500989602704 +rz=-0.0116599432323421 +s=0 +convention=coordinate_frame +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=unitconvert +xy_in=rad +xy_out=deg' --OUTPUT={reproj_path}")




# read csv file monitoring-d8-col-row.csv with cols siteId, col, row
# read csv file rivers-d8-col-row.csv with cols id, startCol, startRow, endCol, endRow

# Read monitoring-d8-col-row.csv
sites_with_raster_coords = []
with open('monitoring-d8-col-row.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader)  # Skip header row
    for row in reader:
        print(row)
        site_id, col, row = row
        sites_with_raster_coords.append([site_id, int(col), int(row)])


# Read rivers-d8-col-row.csv
rivers_with_raster_coords = []
with open('rivers-d8-col-row.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader)  # Skip header row
    for row in reader:
        river_id, startCol, startRow, endCol, endRow = row
        rivers_with_raster_coords.append([river_id, int(startCol), int(startRow), int(endCol), int(endRow)])



for site in sites_with_raster_coords:
    site_id, col, row = site
    name = f'site-{site_id}'
    print(f"generate-catchments.py: Generating catchment for site {site_id}")
    path = f'generated-catchments/{name}.tif'
    polygonize_simplify_reproject(name)


for river in rivers_with_raster_coords:
    river_id, startCol, startRow, endCol, endRow = river
    print(f"generate-catchments.py: Generating catchment for river {river_id}")
    name = f'river-start-{river_id}'
    path = f'generated-catchments/{name}.tif'
    polygonize_simplify_reproject(name)

    name = f'river-end-{river_id}'
    path = f'generated-catchments/{name}.tif'
    polygonize_simplify_reproject(name)


# for every tif file in generated-catchment
# print the file name

