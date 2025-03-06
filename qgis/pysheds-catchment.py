
print('')
print('click point to get catchment')

# iface.addRasterLayer(path, f"catchment-{col}-{row}")
PYSHEDS_DIR = '/mnt/data/gis/catchment/usgs-ui2/pysheds'

def calc_catchment_raster(col, row):
    d8_path = PYSHEDS_DIR + '/data/d8-full.tif'
    out_path = f'{PYSHEDS_DIR}/data/qgis-catchment-{col}-{row}'
    cmd = f'.venv/bin/python catchment.py {d8_path} {col} {row} {out_path}'
    print("--- Exec: ", cmd)
    result = subprocess.check_output(cmd, shell=True, text=True, cwd=PYSHEDS_DIR))
    print("--- Done")
    print(result)

def canvasPressEvent(event):
    layer = iface.activeLayer()
    if layer.type() != QgsMapLayer.RasterLayer:
        print(layer.id(), "is not a raster layer")
        return
        
    extent = layer.dataProvider().extent()
    xres = extent.width() / layer.dataProvider().xSize()
    yres = extent.height() / layer.dataProvider().ySize()
    pos = event.pos()
    point = canvas.getCoordinateTransform().toMapCoordinates(pos.x(), pos.y())
    x = point[0]
    y = point[1]
            
    row = int(math.floor((extent.yMaximum() - y) / yres))
    col = int(math.floor((x - extent.xMinimum()) / xres))
    calc_catchment_raster(row, col)


from qgis.gui import QgsMapToolEmitPoint
canvas = iface.mapCanvas()
pointTool = QgsMapToolEmitPoint(canvas)
pointTool.canvasPressEvent = canvasPressEvent
canvas.setMapTool(pointTool) 


