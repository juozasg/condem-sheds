#!/bin/bash

row0=6057
# numrows = 80
numrows=80

for row in $(seq $row0 $(($row0 + $numrows - 1))); do
	ts=$(find "./tiles" -name "*-$row.webp" | xargs)
	mkdir -p "rows/row-$row"
	# echo montage -tile x1 -geometry +0+0 $ts "rows/row-$row.tif"
	find "./tiles" -name "*-$row.webp" -exec cp {} "rows/row-$row/" \;
done

