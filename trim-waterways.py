#!/usr/bin/env python3

import os
import sys
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

def main():
    # Load waterway features
    waterways = load_waterways()

    # Print information about the first few features
    # print("\nSample of waterway features:")
    # for i, feature in enumerate(waterways[:5]):
    #     geom = feature.GetGeometryRef()
    #     print(f"Feature {i}:")
    #     print(f"  Geometry type: {geom.GetGeometryName()}")
    #     print(f"  Length: {geom.Length():.2f} units")
    #     print(f"  Point count: {geom.GetPointCount()}")

    #     # Print field names and values for this feature
    #     print("  Fields:")
    #     for j in range(feature.GetFieldCount()):
    #         field_name = feature.GetFieldDefnRef(j).GetName()
    #         field_value = feature.GetField(j)
    #         print(f"    {field_name}: {field_value}")
    #     print()

if __name__ == "__main__":
    main()
