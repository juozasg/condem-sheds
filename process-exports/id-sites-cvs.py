# read CSV file and save datasetId and id columns into a dictionary
import csv
import re
import json


path = '/home/juozas/code/SJRBC-web-map-data/datasets.csv'
sites_datasets_id_dict = {}

with open(path, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if 'datasetId' in row and 'id' in row:
            sites_datasets_id_dict[row['datasetId']] = row['id']



def numeric_site_id(site_id):
    # Extract number from filename
    # print(filename)
    match = re.search(r'(\w+)-(\d+)', site_id)
    if match:
        ds = match.group(1)
        id = int(match.group(2))

        dataset_id = int(sites_datasets_id_dict[ds])

        id = dataset_id + id
        # print(f"ID: {id} for {filename}")
        return id
    return 0

# Load the GeoJSON file
geojson_path = '/home/juozas/code/SJRBC-web-map-data/geojson/sites.geojson'
with open(geojson_path, 'r') as f:
    data = json.load(f)

# Process each feature and add the numeric id
features_updated = 0
for feature in data['features']:
    if 'properties' in feature and 'siteId' in feature['properties']:
        site_id = feature['properties']['siteId']
        numeric_id = numeric_site_id(site_id)
        feature['properties']['id'] = numeric_id
        features_updated += 1

# Save the updated GeoJSON back to the same file
with open(geojson_path, 'w') as f:
    json.dump(data, f)

print(f"Added numeric id property to {features_updated} features in {geojson_path}")

