#!/bin/bash

source .venv/bin/activate

# for each file in the catchments directory
for file in generated-catchments/geojson/output/*.geojson; do
		# shave the catchment
		# get file basename
		filename=$(basename -- "$file")
		echo "Shaving $file to generated-catchments/geojson/output/shaved/$filename"
		geojson-shave $file -o "generated-catchments/geojson/output/shaved/$filename"
done
