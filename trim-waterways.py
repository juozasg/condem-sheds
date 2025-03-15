#!/usr/bin/env python3

import os
import sys
import math
import numpy as np
from osgeo import ogr, osr

def load_waterways():
    """
    Load waterway features from a GeoPackage file into a Python list.

    Returns:
        list: A list of OGR feature objects
    """
    # Path to the GeoPackage file
    gpkg_path = "data/waterways-dissolved-good.gpkg"
    layer_name = "waterways-dissolved-good"

    # Check if the file exists
    if not os.path.exists(gpkg_path):
        print(f"Error: File {gpkg_path} not found.")
        sys.exit(1)

    # Open the GeoPackage file
    driver = ogr.GetDriverByName("GPKG")
    data_source = driver.Open(gpkg_path, 0)  # 0 means read-only

    if data_source is None:
        print(f"Error: Could not open {gpkg_path}")
        sys.exit(1)

    # Get the layer
    layer = data_source.GetLayerByName(layer_name)

    if layer is None:
        print(f"Error: Layer '{layer_name}' not found in {gpkg_path}")
        sys.exit(1)

    # Load all features into a list
    features = []
    feature = layer.GetNextFeature()
    while feature:
        # Clone the feature to keep it after the data source is closed
        features.append(feature.Clone())
        feature = layer.GetNextFeature()

    # Print some information about the features
    print(f"Loaded {len(features)} waterway features")

    # Return the list of features
    return features

def find_isolated_endpoints(waterways):
    """
    Find endpoints of waterway lines that don't touch other lines.

    Args:
        waterways: List of OGR feature objects representing waterway lines

    Returns:
        list: List of (x, y) coordinates of isolated endpoints
    """
    # Extract all endpoints from all features
    all_endpoints = []
    endpoint_features = []  # Keep track of which feature each endpoint belongs to

    for i, feature in enumerate(waterways):
        geom = feature.GetGeometryRef()

        # Skip non-line geometries
        if geom.GetGeometryName() not in ['LINESTRING', 'MULTILINESTRING']:
            continue

        # Handle both LINESTRING and MULTILINESTRING
        if geom.GetGeometryName() == 'MULTILINESTRING':
            # For multilinestring, get each component linestring
            for j in range(geom.GetGeometryCount()):
                linestring = geom.GetGeometryRef(j)
                # Get first and last points
                start_point = (linestring.GetX(0), linestring.GetY(0))
                end_point = (linestring.GetX(linestring.GetPointCount()-1), linestring.GetY(linestring.GetPointCount()-1))

                all_endpoints.append(start_point)
                all_endpoints.append(end_point)
                endpoint_features.extend([i, i])
        else:
            # For simple linestring
            start_point = (geom.GetX(0), geom.GetY(0))
            end_point = (geom.GetX(geom.GetPointCount()-1), geom.GetY(geom.GetPointCount()-1))

            all_endpoints.append(start_point)
            all_endpoints.append(end_point)
            endpoint_features.extend([i, i])

    # Find isolated endpoints (those that appear only once in the list)
    isolated_endpoints = []

    # Use a small tolerance for comparing coordinates
    tolerance = 1e-8

    # For each endpoint, check if it's isolated
    for i, (x, y) in enumerate(all_endpoints):
        is_isolated = True
        feature_idx = endpoint_features[i]

        # Compare with all other endpoints
        for j, (other_x, other_y) in enumerate(all_endpoints):
            if i == j:  # Skip comparing with itself
                continue

            # Check if this endpoint is close to another endpoint
            if (abs(x - other_x) < tolerance and abs(y - other_y) < tolerance):
                is_isolated = False
                break

        if is_isolated:
            isolated_endpoints.append((x, y))

    print(f"Found {len(isolated_endpoints)} isolated endpoints out of {len(all_endpoints)} total endpoints")
    return isolated_endpoints

def trim_waterway_lines(waterways, isolated_endpoints, trim_distance=30.0, 
                        output_path="data/trimmed_waterways.gpkg"):
    """
    Trim each waterway line by the specified distance from its isolated endpoint.
    
    Args:
        waterways: List of OGR feature objects representing waterway lines
        isolated_endpoints: List of (x, y) coordinates of isolated endpoints
        trim_distance: Distance in meters to trim from each isolated endpoint
        output_path: Path to save the trimmed features
    """
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Get the spatial reference from the first feature
    source_srs = waterways[0].GetGeometryRef().GetSpatialReference()
    
    # Create the output GeoPackage
    driver = ogr.GetDriverByName("GPKG")
    
    # Remove output file if it exists
    if os.path.exists(output_path):
        driver.DeleteDataSource(output_path)
        
    # Create new data source and layer
    ds = driver.CreateDataSource(output_path)
    layer = ds.CreateLayer("trimmed_waterways", source_srs, ogr.wkbLineString)
    
    # Copy field definitions from the first feature
    feature_defn = waterways[0].GetDefnRef()
    for i in range(feature_defn.GetFieldCount()):
        field_defn = feature_defn.GetFieldDefnRef(i)
        layer.CreateField(field_defn)
    
    # Add a new field to indicate if the line was trimmed
    trimmed_field = ogr.FieldDefn("trimmed", ogr.OFTInteger)
    layer.CreateField(trimmed_field)
    
    # Use a small tolerance for comparing coordinates
    tolerance = 1e-8
    
    # Process each waterway feature
    trimmed_count = 0
    for feature in waterways:
        geom = feature.GetGeometryRef()
        
        # Skip non-line geometries
        if geom.GetGeometryName() not in ['LINESTRING', 'MULTILINESTRING']:
            continue
            
        # Create a new feature for the output
        new_feature = ogr.Feature(layer.GetLayerDefn())
        
        # Copy all field values from the original feature
        for i in range(feature_defn.GetFieldCount()):
            field_name = feature_defn.GetFieldDefnRef(i).GetName()
            new_feature.SetField(field_name, feature.GetField(i))
        
        # Default to not trimmed
        new_feature.SetField("trimmed", 0)
        
        # Handle both LINESTRING and MULTILINESTRING
        if geom.GetGeometryName() == 'MULTILINESTRING':
            # Create a new multilinestring
            new_geom = ogr.Geometry(ogr.wkbMultiLineString)
            
            # Process each component linestring
            for j in range(geom.GetGeometryCount()):
                linestring = geom.GetGeometryRef(j)
                
                # Get first and last points
                start_point = (linestring.GetX(0), linestring.GetY(0))
                end_point = (linestring.GetX(linestring.GetPointCount()-1), linestring.GetY(linestring.GetPointCount()-1))
                
                # Check if either endpoint is isolated
                start_is_isolated = any(abs(start_point[0] - x) < tolerance and 
                                       abs(start_point[1] - y) < tolerance 
                                       for x, y in isolated_endpoints)
                
                end_is_isolated = any(abs(end_point[0] - x) < tolerance and 
                                     abs(end_point[1] - y) < tolerance 
                                     for x, y in isolated_endpoints)
                
                # Trim the linestring if needed
                if start_is_isolated or end_is_isolated:
                    trimmed_linestring = trim_linestring(linestring, 
                                                        start_is_isolated, 
                                                        end_is_isolated, 
                                                        trim_distance)
                    if trimmed_linestring:
                        new_geom.AddGeometry(trimmed_linestring)
                        new_feature.SetField("trimmed", 1)
                        trimmed_count += 1
                else:
                    # Keep the original linestring
                    new_geom.AddGeometry(linestring.Clone())
            
            # Set the geometry for the new feature
            new_feature.SetGeometry(new_geom)
            
        else:  # Simple LINESTRING
            # Get first and last points
            start_point = (geom.GetX(0), geom.GetY(0))
            end_point = (geom.GetX(geom.GetPointCount()-1), geom.GetY(geom.GetPointCount()-1))
            
            # Check if either endpoint is isolated
            start_is_isolated = any(abs(start_point[0] - x) < tolerance and 
                                   abs(start_point[1] - y) < tolerance 
                                   for x, y in isolated_endpoints)
            
            end_is_isolated = any(abs(end_point[0] - x) < tolerance and 
                                 abs(end_point[1] - y) < tolerance 
                                 for x, y in isolated_endpoints)
            
            # Trim the linestring if needed
            if start_is_isolated or end_is_isolated:
                trimmed_linestring = trim_linestring(geom, 
                                                    start_is_isolated, 
                                                    end_is_isolated, 
                                                    trim_distance)
                if trimmed_linestring:
                    new_feature.SetGeometry(trimmed_linestring)
                    new_feature.SetField("trimmed", 1)
                    trimmed_count += 1
            else:
                # Keep the original geometry
                new_feature.SetGeometry(geom.Clone())
        
        # Add the feature to the layer
        layer.CreateFeature(new_feature)
        
        # Clean up
        new_feature = None
    
    # Clean up
    ds = None
    
    print(f"Saved {len(waterways)} waterway features to {output_path}, {trimmed_count} were trimmed")

def trim_linestring(linestring, trim_start, trim_end, trim_distance):
    """
    Trim a linestring by the specified distance from its endpoints.
    
    Args:
        linestring: OGR linestring geometry
        trim_start: Boolean indicating whether to trim from the start
        trim_end: Boolean indicating whether to trim from the end
        trim_distance: Distance in meters to trim
        
    Returns:
        Trimmed OGR linestring geometry or None if the line is too short
    """
    point_count = linestring.GetPointCount()
    
    if point_count < 2:
        return None
    
    # Create a new linestring
    new_linestring = ogr.Geometry(ogr.wkbLineString)
    
    # Calculate the total length of the linestring
    total_length = linestring.Length()
    
    # If the line is shorter than the trim distance, return None
    if total_length <= trim_distance and (trim_start or trim_end):
        return None
    
    # If we're not trimming, just return a clone
    if not trim_start and not trim_end:
        return linestring.Clone()
    
    # Determine the start and end indices for the new linestring
    start_idx = 0
    end_idx = point_count - 1
    
    if trim_start:
        # Find the point along the line that is trim_distance from the start
        distance_from_start = 0.0
        for i in range(1, point_count):
            x1, y1 = linestring.GetX(i-1), linestring.GetY(i-1)
            x2, y2 = linestring.GetX(i), linestring.GetY(i)
            
            segment_length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            distance_from_start += segment_length
            
            if distance_from_start >= trim_distance:
                # Interpolate to find the exact point
                excess = distance_from_start - trim_distance
                ratio = excess / segment_length
                
                # Calculate the interpolated point
                x = x2 - ratio * (x2 - x1)
                y = y2 - ratio * (y2 - y1)
                
                # Add this point as the new start
                new_linestring.AddPoint(x, y)
                start_idx = i
                break
    
    if trim_end:
        # Find the point along the line that is trim_distance from the end
        distance_from_end = 0.0
        for i in range(point_count - 1, 0, -1):
            x1, y1 = linestring.GetX(i), linestring.GetY(i)
            x2, y2 = linestring.GetX(i-1), linestring.GetY(i-1)
            
            segment_length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            distance_from_end += segment_length
            
            if distance_from_end >= trim_distance:
                # Interpolate to find the exact point
                excess = distance_from_end - trim_distance
                ratio = excess / segment_length
                
                # Calculate the interpolated point
                x = x1 + ratio * (x2 - x1)
                y = y1 + ratio * (y2 - y1)
                
                # This will be the new end point
                end_idx = i - 1
                break
    
    # Add points to the new linestring
    if not trim_start:
        new_linestring.AddPoint(linestring.GetX(0), linestring.GetY(0))
    
    for i in range(start_idx, end_idx + 1):
        if i == start_idx and trim_start:
            # Skip, we already added the interpolated start point
            continue
        new_linestring.AddPoint(linestring.GetX(i), linestring.GetY(i))
    
    if trim_end and end_idx < point_count - 1:
        # Add the interpolated end point
        x1, y1 = linestring.GetX(end_idx), linestring.GetY(end_idx)
        x2, y2 = linestring.GetX(end_idx + 1), linestring.GetY(end_idx + 1)
        
        distance_from_end = 0.0
        for i in range(point_count - 1, end_idx, -1):
            xa, ya = linestring.GetX(i), linestring.GetY(i)
            xb, yb = linestring.GetX(i-1), linestring.GetY(i-1)
            segment_length = math.sqrt((xb - xa)**2 + (yb - ya)**2)
            distance_from_end += segment_length
        
        excess = distance_from_end - trim_distance
        segment_length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        ratio = excess / segment_length
        
        x = x1 + ratio * (x2 - x1)
        y = y1 + ratio * (y2 - y1)
        
        new_linestring.AddPoint(x, y)
    
    # Check if the resulting linestring has at least 2 points
    if new_linestring.GetPointCount() < 2:
        return None
    
    return new_linestring

def save_endpoints_to_gpkg(endpoints, source_gpkg_path="data/waterways-dissolved-good.gpkg",
                          output_path="data/isolated_endpoints.gpkg"):
    """
    Save the isolated endpoints to a GeoPackage file with the same CRS as the source file.

    Args:
        endpoints: List of (x, y) coordinates
        source_gpkg_path: Path to the source GeoPackage file to get CRS from
        output_path: Path to save the GeoPackage file
    """
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Get the spatial reference from the source file
    source_driver = ogr.GetDriverByName("GPKG")
    source_ds = source_driver.Open(source_gpkg_path, 0)  # 0 means read-only
    source_layer = source_ds.GetLayerByName("waterways-dissolved-good")
    source_srs = source_layer.GetSpatialRef()

    # Create the output GeoPackage
    driver = ogr.GetDriverByName("GPKG")

    # Remove output file if it exists
    if os.path.exists(output_path):
        driver.DeleteDataSource(output_path)

    # Create new data source and layer
    ds = driver.CreateDataSource(output_path)
    layer = ds.CreateLayer("isolated_endpoints", source_srs, ogr.wkbPoint)

    # Add an ID field
    id_field = ogr.FieldDefn("id", ogr.OFTInteger)
    layer.CreateField(id_field)

    # Create features for each endpoint
    for i, (x, y) in enumerate(endpoints):
        # Create a point geometry
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(x, y)

        # Create a feature
        feature = ogr.Feature(layer.GetLayerDefn())
        feature.SetGeometry(point)
        feature.SetField("id", i)

        # Add the feature to the layer
        layer.CreateFeature(feature)

        # Clean up
        feature = None

    # Clean up
    ds = None
    source_ds = None

    print(f"Saved {len(endpoints)} isolated endpoints to {output_path}")

def main():
    # Load waterway features
    waterways = load_waterways()

    # Find isolated endpoints
    isolated_endpoints = find_isolated_endpoints(waterways)

    # Save isolated endpoints to a GeoPackage file
    save_endpoints_to_gpkg(isolated_endpoints)

    # Trim waterway lines from isolated endpoints and save to a new file
    trim_waterway_lines(waterways, isolated_endpoints, 30.0)

    # Print the first few isolated endpoints
    print("\nSample of isolated endpoints (x, y):")
    for i, (x, y) in enumerate(isolated_endpoints[:10]):
        print(f"{i}: ({x:.6f}, {y:.6f})")

if __name__ == "__main__":
    main()
