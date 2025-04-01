import os
import geopandas as gpd
import argparse
from pathlib import Path

def count_features_in_geojsons(folder_path):
    """
    Count and print the number of features in each GeoJSON file in the specified folder.

    Parameters:
    -----------
    folder_path : str
        Path to the folder containing GeoJSON files
    """
    folder = Path(folder_path)

    # Check if folder exists
    if not folder.exists() or not folder.is_dir():
        print(f"Error: {folder_path} is not a valid directory")
        return

    # Get all geojson files
    geojson_files = list(folder.glob("*.geojson"))

    if not geojson_files:
        print(f"No GeoJSON files found in {folder_path}")
        return

    print(f"Found {len(geojson_files)} GeoJSON files in {folder_path}")
    print("-" * 50)

    first = True
    # Loop through each GeoJSON file and count features
    for geojson_file in sorted(geojson_files):
        try:
            gdf = gpd.read_file(geojson_file)
            feature_count = len(gdf)
            print(f"{geojson_file.name}: {feature_count} features")
            if first:
                print(gdf.head())
                print("-" * 50)
                print(gdf)
                first = False
        except Exception as e:
            print(f"{geojson_file.name}: Error reading file - {str(e)}")

    print("-" * 50)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Count features in GeoJSON files")
    parser.add_argument("folder", help="Path to folder containing GeoJSON files")
    args = parser.parse_args()

    count_features_in_geojsons(args.folder)