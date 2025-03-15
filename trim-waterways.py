#!/usr/bin/env python3

import os
import sys
import numpy as np
from osgeo import ogr

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

def main():
    # Load waterway features
    waterways = load_waterways()
    
    # Find isolated endpoints
    isolated_endpoints = find_isolated_endpoints(waterways)
    
    # Print the first few isolated endpoints
    print("\nSample of isolated endpoints (x, y):")
    for i, (x, y) in enumerate(isolated_endpoints[:10]):
        print(f"{i}: ({x:.6f}, {y:.6f})")

if __name__ == "__main__":
    main()
