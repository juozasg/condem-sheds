import json
import glob
import os
import re


# read CSV file and save datasetId and id columns into a dictionary
import csv
path = '/home/juozas/code/SJRBC-web-map-data/datasets.csv'
sites_datasets_id_dict = {}

with open(path, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if 'datasetId' in row and 'id' in row:
            sites_datasets_id_dict[row['datasetId']] = row['id']


# Find all geojson files matching the pattern
# file_pattern = '/home/juozas/code/SJRBC-web-map-data/geojson/catchments/river-end-*.geojson'
file_pattern = '/home/juozas/code/SJRBC-web-map-data/geojson/catchments/site-*.geojson'
catchment_files = glob.glob(file_pattern)

# Extract ID from filenames and sort files numerically
def extract_id_simple(filename):
    # Extract number from filename
    match = re.search(r'river-end-(\d+)\.geojson', filename)
    if match:
        return int(match.group(1))
    return 0

def extract_numeric_id_site(filename):
    # Extract number from filename
    # print(filename)
    match = re.search(r'site-(\w+)-(\d+)\.geojson', filename)
    if match:
        ds = match.group(1)
        id = int(match.group(2))

        dataset_id = int(sites_datasets_id_dict[ds])

        id = dataset_id + id
        # print(f"ID: {id} for {filename}")
        return id
    return 0


def site_id(filename):
    match = re.search(r'site-(\w+)-(\d+)\.geojson', filename)
    if match:
        return match.group(1) + '-' + match.group(2)



# Sort files numerically by ID
# catchment_files.sort(key=extract_id_simple)
catchment_files.sort(key=extract_numeric_id_site)

print(f"Found {len(catchment_files)} files")

# Prepare merged feature collection
merged_features = []

# Process each file
for file_path in catchment_files:
    # Extract ID from filename
    feature_id = extract_numeric_id_site(file_path)
    # feature_id = extract_id_simple(file_path)
    print(f"Processing {file_path} with ID {feature_id}")

    # Load GeoJSON from file
    with open(file_path, 'r') as f:
        data = json.load(f)

    # Assuming each file has a single feature in a FeatureCollection
    if 'features' in data and len(data['features']) > 0:
        feature = data['features'][0]

        # Add ID property to the feature
        if 'properties' not in feature:
            feature['properties'] = {}
        feature['properties']['id'] = int(feature_id)
        feature['properties']['siteId'] = site_id(file_path)

        # Add to our merged collection
        merged_features.append(feature)

# Create the final merged GeoJSON
merged_geojson = {
    "type": "FeatureCollection",
    "features": merged_features
}

# Write the merged GeoJSON to file
output_file = 'site-catchments.geojson'
with open(output_file, 'w') as f:
    json.dump(merged_geojson, f)

print(f"Successfully merged {len(merged_features)} features into {output_file}")