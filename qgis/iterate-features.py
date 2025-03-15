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
    text_id.setText(str(ID))

def reset_id():
    global ID
    global layer
    ID = 0
    text_id.setText('0')
    layer = iface.activeLayer()
    canvas.zoomToFeatureIds(layer, [ID])

## ACTIONS
zoom_next_action = QAction("Zoom Next")
zoom_next_action.triggered.connect(zoom_next)

zoom_prev_action = QAction("Zoom Previous")
zoom_prev_action.triggered.connect(zoom_prev)

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
zoom_toolbar.addWidget(label)
zoom_toolbar.addWidget(text_id)

iface.layerTreeView().currentLayerChanged.connect(reset_id)
