import os


exec(open(os.path.dirname(os.path.abspath(__file__)) + '/river_utils.py').read())

river = setup_taggable_rivers_layer() # this is loaded from the river_utils.py file

# Get features with NULL catchment_lat values
untagged_features = []
for feature in river.getFeatures():
    if feature['catchment_lat'] is NULL:  # NULL is a special QGIS constant
        untagged_features.append(feature)

print(f"Found {len(null_features)} features with NULL catchment_lat values")

