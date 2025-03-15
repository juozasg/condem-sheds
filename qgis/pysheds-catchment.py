import os
import subprocess
print('')
print('click point to get catchment')

exec(open(os.path.dirname(os.path.abspath(__file__)) + '/river_utils.py').read())


# 
PYSHEDS_DIR = '/mnt/data/gis/catchment/usgs-ui2/pysheds'

def calc_catchment_raster(col, row):
    d8_path = PYSHEDS_DIR + '/data/d8-full.tif'
    out_path = f'{PYSHEDS_DIR}/data/qgis-catchment-{col}-{row}.tif'
    cmd = f'.venv/bin/python catchment.py {d8_path} {col} {row} {out_path}'
    print("--- Exec: ", cmd)
    result = subprocess.check_output(cmd, shell=True, text=True, cwd=PYSHEDS_DIR)
    print(result)
    print("--- Done. Adding raster ", out_path)
    l = iface.addRasterLayer(out_path, f"catchment-{col}-{row}")
    l.setOpacity(0.3)




def canvasPressEvent(event):
    layer = iface.activeLayer()
    if layer.type() != QgsMapLayer.RasterLayer:
        print(layer.id(), "is not a raster layer")
        return
        
    pos = event.pos()
    col, row = pos_to_col_row(layer, pos)

    calc_catchment_raster(col, row)


from qgis.gui import QgsMapToolEmitPoint
canvas = iface.mapCanvas()
pointTool = QgsMapToolEmitPoint(canvas)
pointTool.canvasPressEvent = canvasPressEvent
canvas.setMapTool(pointTool) 


