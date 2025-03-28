#!/bin/bash

source .venv/bin/activate

# for each file in the catchments directory
for file in generated-catchments/geojson/output/*.geojson; do
		# shave the catchment
		echo "Shaving $file"
		# geojson-shave $file
done