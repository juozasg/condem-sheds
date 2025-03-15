import os
import sys
import numpy as np
from osgeo import gdal, ogr, osr
from shapely.geometry import LineString, Point
from shapely.ops import split, nearest_points
from shapely.wkt import loads
import math

waterways_file = "/mnt/data/gis/catchment/usgs-ui2/pysheds/data/waterways-trimmed.gpkg"
waterways_layer = "waterways-trimmed"

gwater_file = '/mnt/data/gis/catchment/usgs-ui2/pysheds/data/gwater-norm-3160.tif'
output_file = "/mnt/data/gis/catchment/usgs-ui2/pysheds/data/waterways-near-gwater.gpkg"

def split_line_by_distance(line, distance):
    """Split a line into segments of specified distance."""
    segments = []
    line_length = line.length
    
    # If line is shorter than the segment length, return it as is
    if line_length <= distance:
        return [line]
    
    # Calculate number of segments
    num_segments = math.ceil(line_length / distance)
    
    # Create points at regular intervals
    points = [line.interpolate(i * distance / num_segments, normalized=True) 
              for i in range(num_segments + 1)]
    
    # Create segments between consecutive points
    for i in range(len(points) - 1):
        segment = LineString([points[i], points[i+1]])
        segments.append(segment)
    
    return segments

def is_near_water_pixel(line, raster_data, geotransform, search_distance=30.0):
    """Check if a line is within search_distance of a water pixel (value == 1)."""
    # Get the bounding box of the line with buffer
    minx, miny, maxx, maxy = line.buffer(search_distance).bounds
    
    # Convert to pixel coordinates
    px_min = int((minx - geotransform[0]) / geotransform[1])
    py_min = int((maxy - geotransform[3]) / geotransform[5])  # Note: geotransform[5] is negative
    px_max = int((maxx - geotransform[0]) / geotransform[1])
    py_max = int((miny - geotransform[3]) / geotransform[5])
    
    # Ensure we're within the raster bounds
    px_min = max(0, px_min)
    py_min = max(0, py_min)
    px_max = min(raster_data.shape[1] - 1, px_max)
    py_max = min(raster_data.shape[0] - 1, py_max)
    
    # Extract the subset of the raster
    subset = raster_data[py_min:py_max+1, px_min:px_max+1]
    
    # Check if any pixel has value 1
    if np.any(subset == 1):
        return True
    
    return False

def main():
    # Open the groundwater raster
    gwater_ds = gdal.Open(gwater_file)
    if gwater_ds is None:
        print(f"Error: Could not open {gwater_file}")
        return
    
    # Get raster data and geotransform
    gwater_band = gwater_ds.GetRasterBand(1)
    gwater_data = gwater_band.ReadAsArray()
    geotransform = gwater_ds.GetGeoTransform()
    
    # Open the waterways vector file
    driver = ogr.GetDriverByName("GPKG")
    waterways_ds = driver.Open(waterways_file, 0)  # 0 means read-only
    if waterways_ds is None:
        print(f"Error: Could not open {waterways_file}")
        return
    
    waterways = waterways_ds.GetLayerByName(waterways_layer)
    if waterways is None:
        print(f"Error: Could not find layer {waterways_layer}")
        return
    
    # Create output file
    if os.path.exists(output_file):
        driver.DeleteDataSource(output_file)
    
    out_ds = driver.CreateDataSource(output_file)
    out_layer = out_ds.CreateLayer("waterways-near-gwater", waterways.GetSpatialRef(), ogr.wkbLineString)
    
    # Copy field definitions
    layer_defn = waterways.GetLayerDefn()
    for i in range(layer_defn.GetFieldCount()):
        field_defn = layer_defn.GetFieldDefn(i)
        out_layer.CreateField(field_defn)
    
    # Add a new field to indicate it's near water
    near_water_field = ogr.FieldDefn("near_water", ogr.OFTInteger)
    out_layer.CreateField(near_water_field)
    
    # Process each waterway
    segment_distance = 5.0  # 5 meters
    search_distance = 30.0  # 30 meters
    
    waterways.ResetReading()
    feature_count = waterways.GetFeatureCount()
    processed = 0
    
    for feature in waterways:
        processed += 1
        if processed % 100 == 0:
            print(f"Processing feature {processed}/{feature_count}")
        
        # Get the geometry
        geom = feature.GetGeometryRef()
        if geom is None:
            continue
        
        # Convert to shapely
        line = loads(geom.ExportToWkt())
        
        # Split the line into segments
        segments = split_line_by_distance(line, segment_distance)
        
        # Check each segment
        for segment in segments:
            if is_near_water_pixel(segment, gwater_data, geotransform, search_distance):
                # Create a new feature
                out_feature = ogr.Feature(out_layer.GetLayerDefn())
                
                # Copy attributes from original feature
                for i in range(layer_defn.GetFieldCount()):
                    out_feature.SetField(i, feature.GetField(i))
                
                # Set the near_water field
                out_feature.SetField("near_water", 1)
                
                # Set the geometry
                out_feature.SetGeometry(ogr.CreateGeometryFromWkt(segment.wkt))
                
                # Add to output layer
                out_layer.CreateFeature(out_feature)
                out_feature = None
    
    # Clean up
    waterways_ds = None
    out_ds = None
    gwater_ds = None
    
    print(f"Completed processing. Results saved to {output_file}")

if __name__ == "__main__":
    main()
