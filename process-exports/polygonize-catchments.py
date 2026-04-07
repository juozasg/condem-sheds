import csv
import os

# NOTE: if files exist gdal will concateneta them and duplicate features. use force=True to delete everything after first run

def polygonize_simplify_reproject(name, force=False):
    input_path = f'generated-catchments/{name}.tif'
    polygon_path = f'generated-catchments/geojson/{name}.poly.geojson'
    simp_path = f'generated-catchments/geojson/{name}.simp.geojson'
    reproj_path = f'generated-catchments/geojson/output/{name}.geojson'

    force = True

    if force:
        os.system(f'rm -f {reproj_path}')
        os.system(f'rm -f {simp_path}')
        os.system(f'rm -f {polygon_path}')

    if not os.path.isfile(reproj_path):
        print("---POLYGONIZE---")
        os.system(f'gdal_polygonize.py {input_path} -8 -f geojson {polygon_path}')

        print("---SIMPLIFY---")
        os.system(f'qgis_process run native:simplifygeometries --distance_units=meters --area_units=m2 --ellipsoid=EPSG:7019 --INPUT={polygon_path} --METHOD=0 --TOLERANCE=10 --OUTPUT={simp_path}')

        print("---REPROJ---")
        os.system(f"qgis_process run native:reprojectlayer --distance_units=meters --area_units=m2 --ellipsoid=EPSG:7019 --INPUT={simp_path} --TARGET_CRS='EPSG:4326' --CONVERT_CURVED_GEOMETRIES=false --OPERATION='+proj=pipeline +step +inv +proj=utm +zone=16 +ellps=GRS80 +step +proj=push +v_3 +step +proj=cart +ellps=GRS80 +step +proj=helmert +x=-0.991 +y=1.9072 +z=0.5129 +rx=-0.0257899075194932 +ry=-0.0096500989602704 +rz=-0.0116599432323421 +s=0 +convention=coordinate_frame +step +inv +proj=cart +ellps=WGS84 +step +proj=pop +v_3 +step +proj=unitconvert +xy_in=rad +xy_out=deg' --OUTPUT={reproj_path}")
        print("\n")


# Read monitoring-d8-col-row.csv
sites = []
with open('monitoring-d8-col-row.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader)  # Skip header row
    for row in reader:
        print(row)
        site_id, col, row = row
        sites.append(site_id)


# # Read rivers-d8-col-row.csv
# rivers = []
# with open('rivers-d8-col-row.csv', 'r') as f:
#     reader = csv.reader(f)
#     next(reader)  # Skip header row
#     for row in reader:
#         river_id, startCol, startRow, endCol, endRow = row
#         rivers.append(river_id)



for site_id in sites:
    name = f'site-{site_id}'
    print(f"generate-catchments.py: Generating catchment for site {site_id}")
    path = f'generated-catchments/{name}.tif'
    polygonize_simplify_reproject(name)



# for river_id in rivers:
#     print(f"generate-catchments.py: Generating catchment for river {river_id}")
#     name = f'river-start-{river_id}'
#     path = f'generated-catchments/{name}.tif'
#     polygonize_simplify_reproject(name)

#     name = f'river-end-{river_id}'
#     path = f'generated-catchments/{name}.tif'
#     polygonize_simplify_reproject(name)


# for every tif file in generated-catchment
# print the file name

