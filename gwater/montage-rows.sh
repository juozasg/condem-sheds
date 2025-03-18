# #!/bin/bash

row0=6057
# numrows = 80
numrows=80

for row in $(seq $row0 $(($row0 + $numrows - 1))); do
	# ts=$(find "./tiles" -name "*-$row.webp" | xargs)
# ts=$(find "./tiles" -name "*-$row.webp" | xargs)
	cd "rows/row-$row"
	echo montage -tile x1 -geometry +0+0 *.webp "montage-$row.tif"
	montage -tile x1 -geometry +0+0 *.webp "montage-$row.tif"
	cd ../..
done

# the whole shebang
# montage -monitor -tile 1x -geometry +0+0 $rows tiff64:gwater.tif
