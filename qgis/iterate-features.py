layer = iface.activeLayer()
canvas = iface.mapCanvas()
ID = 0

def zoom_next():
    global ID
    ID += 1
    zoom(ID)
    
def zoom_prev():
    global ID
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

## TOOLBAR
zoom_toolbar = iface.addToolBar("Zoom Features")
zoom_toolbar.addAction(zoom_prev_action)
zoom_toolbar.addAction(zoom_next_action)
zoom_toolbar.addWidget(label)
zoom_toolbar.addWidget(text_id)

iface.layerTreeView().currentLayerChanged.connect(reset_id)