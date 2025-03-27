# this is a QGIS script
# It is not a standalone script
raster = QgsProject.instance().mapLayersByName('d8')[0]

monitoring = QgsProject.instance().mapLayersByName('monitoring')[0]
flow_usgs = QgsProject.instance().mapLayersByName('flow-usgs')[0]
flow_tolthawk = QgsProject.instance().mapLayersByName('flow-tolthawk')[0]

rivers = list(QgsProject.instance().mapLayersByName('rivers')[0].getFeatures())

sites = list(monitoring.getFeatures()) + list(flow_usgs.getFeatures()) + list(flow_tolthawk.getFeatures())
sites_with_raster_coords = []
rivers_with_raster_coords = []

# print(sites)
# exit()

def pos_to_col_row(layer, point):
    extent = layer.dataProvider().extent()
    xres = extent.width() / layer.dataProvider().xSize()
    yres = extent.height() / layer.dataProvider().ySize()
    x = point[0]
    y = point[1]

    row = int(math.floor((extent.yMaximum() - y) / yres))
    col = int(math.floor((x - extent.xMinimum()) / xres))
    return col, row


def get_line_first_or_last_vertex(geometry, first=True):
    # Get the vertices of the LineString
    vertices = list(geometry.vertices())
    # Choose the vertex to zoom to
    vertex = vertices[0] if first else vertices[-1]
    return vertex

for site in sites:
    # sites are Point features
    # get point
    geom = site.geometry()
    point = geom.asPoint()
    col, row = pos_to_col_row(raster, point)

    siteId = site['siteId']
    sites_with_raster_coords.append((siteId, col, row))

for river in rivers:
    # rivers are LineString features
    # get line
    geom = river.geometry()
    fpoint = qgis.core.QgsPointXY(get_line_first_or_last_vertex(geom, first=True))
    fcol, frow = pos_to_col_row(raster, fpoint)

    lpoint = qgis.core.QgsPointXY(get_line_first_or_last_vertex(geom, first=False))
    lcol, lrow = pos_to_col_row(raster, lpoint)

    rid = river['id']
    rivers_with_raster_coords.append((rid, fcol, frow, lcol, lrow))

# write to csv
import csv
# with open('monitoring-d8-col-row.csv', 'w') as f:
#     writer = csv.writer(f)
#     writer.writerow(['siteId', 'col', 'row'])
#     for site in sites_with_raster_coords:
#         writer.writerow(site)

with open('rivers-d8-col-row.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['id', 'startCol', 'startRow', 'endCol', 'endRow'])
    for river in rivers_with_raster_coords:
        writer.writerow(river)