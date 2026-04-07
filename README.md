
## condem-sheds
Codes to generate catchments for water monitoring sites for St. Joseph Basin River Data Explorer (https://github.com/juozasg/river-data-explorer)


## Overview

[pysheds](https://github.com/pysheds/pysheds) is used to generate catchment shapes (geojson polygons) for monitoring sites (points) the St. Joe River basin.

pysheds inputs are a D8 flow raster (geotiff) and site pixel index coordinates (col, row) in the D8 raster. The output is a catchment shape raster (geotiff) in the same CRS as the D8 raster. We use `EPSG:3160 - NAD83(CSRS) / UTM zone 16N` here.


## Running it

To get site pixel index coordinates (col, row) or (x,y) for sites, a QGIS script `d8-coords.py` must be run. It will dump pixel coords for specified features into a `monitoring-d8-col-row.csv` file that gets fed into `pysheds`. It will use `d8` raster layer in QGIS as the reference. Each site must be placed on a meaningful accumulation flow line pixel to have a meaningful catchment (see `condem.py`).

`generate-catchments.py` will use the same `d8` raster and the generated `monitoring-d8-col-row.csv` to calculate catchment geotiffs for each site.

`polygonize-catchment.py` takes each catchment geotiff raster and will polygonize it, projected it to `EPSG:4326` (lat, lon), then  simplify the geometry and then save it as a geojson polygon.

`shave-catchments.sh` will reduce the length of floating points ASCII in geojson files to reduce file size.



## D8 and accumulation flow

`condem.py` takes a DEM (elevation raster), conditions it to make sense for a hydrological model, then calculates a D8 raster and an accumulation flow lines raster.


## qpysheds

`qpysheds` folder contains a QGIS plugin that makes it easier to edit a large list of point (sites) or line (rivers) features to move each point on meaninful accumulation flow lines.




