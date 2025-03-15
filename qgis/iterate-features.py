from qgis.PyQt.QtWidgets import QAction, QLabel, QLineEdit
from qgis.PyQt.QtCore import QSize
from qgis.core import QgsProject, QgsVectorLayer, QgsFeature

layer = iface.activeLayer()
canvas = iface.mapCanvas()
ID = 0

def zoom_next():
    global ID
    global layer
    ID += 1
    # Wrap around to the first feature if we've gone past the last one
    if ID >= layer.featureCount():
        ID = 1
    zoom(ID)

def zoom_prev():
    global ID
    global layer
    if ID <= 0:
        # Wrap around to the last feature
        feature_count = layer.featureCount()
        ID = feature_count - 1
    else:
        ID -= 1
    zoom(ID)

def zoom(ID):
    canvas.zoomToFeatureIds(layer, [ID])
    # Select the feature
    layer.selectByIds([ID])
    text_id.setText(str(ID))

def reset_id():
    global ID
    global layer
    ID = 0
    text_id.setText('0')
    layer = iface.activeLayer()
    canvas.zoomToFeatureIds(layer, [ID])

def copy_to_tagged():
    global ID
    global layer
    
    # Check if the tagged layer exists
    tagged_layer = QgsProject.instance().mapLayersByName('tagged')
    if not tagged_layer:
        iface.messageBar().pushMessage("Error", "Layer 'tagged' not found", level=1)
        return
    
    tagged_layer = tagged_layer[0]
    
    # Get the current feature
    feature = next(layer.getFeatures(f"$id = {ID}"), None)
    if not feature:
        iface.messageBar().pushMessage("Error", "Feature not found", level=1)
        return
    
    # Create a new feature with the same geometry
    new_feature = QgsFeature(tagged_layer.fields())
    new_feature.setGeometry(feature.geometry())
    
    # Copy attributes if field names match
    for field_name in layer.fields().names():
        if tagged_layer.fields().indexOf(field_name) >= 0:
            new_feature[field_name] = feature[field_name]
    
    # Add the feature to the tagged layer
    tagged_layer.startEditing()
    tagged_layer.addFeature(new_feature)
    tagged_layer.commitChanges()
    
    iface.messageBar().pushMessage("Success", "Feature copied to 'tagged' layer", level=3, duration=3)

## ACTIONS
zoom_next_action = QAction("Zoom Next")
zoom_next_action.triggered.connect(zoom_next)

zoom_prev_action = QAction("Zoom Previous")
zoom_prev_action.triggered.connect(zoom_prev)

copy_action = QAction("Copy to Tagged")
copy_action.triggered.connect(copy_to_tagged)

label = QLabel("ID:")
text_id = QLineEdit()
text_id.setMaximumSize(QSize(40, 100))
text_id.setText('0')

def jump_to_id():
    global ID
    global layer
    try:
        new_id = int(text_id.text())
        # Ensure ID is within valid range
        feature_count = layer.featureCount()
        if new_id >= feature_count:
            new_id = feature_count - 1
        elif new_id < 0:
            new_id = 0
        ID = new_id
        zoom(ID)
    except ValueError:
        # If text is not a valid integer, reset to current ID
        text_id.setText(str(ID))

# Connect the editingFinished signal to jump_to_id function
text_id.editingFinished.connect(jump_to_id)

## TOOLBAR
zoom_toolbar = iface.addToolBar("Zoom Features")
zoom_toolbar.addAction(zoom_prev_action)
zoom_toolbar.addAction(zoom_next_action)
zoom_toolbar.addAction(copy_action)
zoom_toolbar.addWidget(label)
zoom_toolbar.addWidget(text_id)

iface.layerTreeView().currentLayerChanged.connect(reset_id)
