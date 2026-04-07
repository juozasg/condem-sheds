
# condem-sheds
A set of codes to generate watershed catchment polygons for water monitoring sites for [St. Joseph Basin River Data Explorer](https://github.com/juozasg/river-data-explorer)


## Overview
[pysheds](https://github.com/pysheds/pysheds) is used to generate catchment shapes (geojson polygons) for monitoring sites (points) in the St. Joe River basin.

pysheds inputs are a D8 flow raster (geotiff) and site pixel index coordinates (col, row) in the D8 raster. The output is a catchment shape raster (geotiff) in the same CRS as the D8 raster. We use `EPSG:3160 - NAD83(CSRS) / UTM zone 16N` for catchment calculations before converting to `EPSG:4326` (lat, lon) coordinates for web mapping.


## Running it
To get site pixel index coordinates (col, row) or (x, y) for sites the QGIS script `qgis-d8-coords.py` must be run by copying it in QGIS Python Console. It will dump pixel coords for specified features into a `monitoring-d8-col-row.csv` file that gets fed into `pysheds`. QGIS `d8` raster layer is used to calculate pixel indexes. Each site must be placed on a meaningful accumulation flow line pixel to have a meaningful catchment (see `condem.py`).

`generate-catchments.py` will use the same `d8` raster and the generated `monitoring-d8-col-row.csv` to calculate catchment geotiffs for each site.

`process-exports/polygonize-catchment.py` takes each catchment geotiff raster and will polygonize it, projected it to `EPSG:4326` (lat, lon), then  simplify the geometry and then save it as a geojson polygon. `monitoring-d8-col-row.csv` provides the list of sites (and rivers) to process. **system or QGIS python must be used, not .venv python - for QGIS/GDAL**

`shave-catchments.sh` will reduce the length of floating points ASCII in geojson files to reduce file size.


## Data packaging
[St. Joseph Basin River Data Explorer](https://github.com/juozasg/river-data-explorer) uses data packages stored in the [SJRBC-web-map-data](https://github.com/Limnogirl90/SJRBC-web-map-data) data repo. The `geojson` folder contains all the features used for the interactive map.

`process-exports/merge-cachments.py` merges `site-*.geojson` catchment shape files into a single `site-cachments.geojson` file wih correct ID metadata for each feature.


## D8 and accumulation flow
`condem.py` takes a DEM (elevation raster), conditions it to make sense for a hydrological model, then calculates a D8 raster and an accumulation flow lines raster.


## qpysheds
`qpysheds` folder contains a QGIS plugin that makes it easier to edit a large list of point (sites) or line (rivers) features to move each point on meaninful accumulation flow lines.





## Non-catchment data packaging
`process-exports/id-sites-geojson.py` will process `exports/sites.geojson` feature collection to add a numerical ID for each site string ID. For example `elkhart-1` will be numbered as `20001`. Numeric IDs are required for fast feature state queries in the `maplibre-gl` mapping library. After shaving the output geojson `sites-with-id.geojson` should be renamed to singular `site.geojson` for the data package.