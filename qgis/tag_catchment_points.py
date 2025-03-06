import os
import time
from PyQt5.QtCore import QThread, pyqtSignal


canvas = iface.mapCanvas()

exec(open(os.path.dirname(os.path.abspath(__file__)) + '/river_utils.py').read())

# delete a layer named 'rivers with cpoints' if it exists
if QgsProject.instance().mapLayersByName('rivers with cpoints'):
    old = QgsProject.instance().mapLayersByName('rivers with cpoints')[0]
    QgsProject.instance().removeMapLayer(old.id())


river = setup_taggable_rivers_layer() # this is loaded from the river_utils.py file
# select the river layer
# QgsProject.instance().setActiveLayer(river)

# Get features with NULL catchment_lat values
untagged_features = []
for feature in river.getFeatures():
    if feature['catchment_lat'] is None:  
        untagged_features.append(feature)

print(f"Found {len(untagged_features)} features with NULL catchment_lat values")

target = None

def next_untagged_feature():
    global target
    target = untagged_features.pop(0)
    transform_and_zoom_extent(river.crs(), target.geometry().boundingBox())
    river.selectByIds([target.id()])
    print("feature:", target.id(), target['name'])



next_untagged_feature()


# for each untagged feature, zoom to the feature
# QgsProject.instance().setActiveLayer(river)
# for feature in untagged_features:
# select the feature by id


clat_idx = river.fields().indexOf('catchment_lat')
clon_idx = river.fields().indexOf('catchment_lon')
ccol_idx = river.fields().indexOf('catchment_col')
crow_idx = river.fields().indexOf('catchment_row')

d8_layer = QgsProject.instance().mapLayersByName('d8-full')[0]
print("col, row reference layer =", d8_layer.name())

def tag_selected_feature_coords(event):
    # get the coordinates of the clicked point
    pos = event.pos()
    
    # transform pos
    lon, lat = pos_to_lonlat(pos)
    col, row = pos_to_col_row(d8_layer, pos)

    print("coords: ", lon, lat, col, row)

    # update the feature with the new coordinates
    # target.setAttribute('catchment_lon', lon)
    # target.setAttribute('catchment_lat', lat)
    # target.setAttribute('catchment_col', col)
    # target.setAttribute('catchment_row', row)

    with edit(river):
        river.changeAttributeValue(target.id(), clat_idx, lat)
        river.changeAttributeValue(target.id(), clon_idx, lon)
        river.changeAttributeValue(target.id(), ccol_idx, col)
        river.changeAttributeValue(target.id(), crow_idx, row)
    # target.commitChanges()

    # next feature
    next_untagged_feature()
   
from qgis.gui import QgsMapToolEmitPoint
canvas = iface.mapCanvas()
pointTool = QgsMapToolEmitPoint(canvas)
pointTool.canvasPressEvent = tag_selected_feature_coords
canvas.setMapTool(pointTool) 

