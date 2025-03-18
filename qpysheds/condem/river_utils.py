from qgis.core import QgsProject, QgsCoordinateTransform, QgsField
from qgis.PyQt.QtCore import QVariant

def transform_and_zoom_extent(source_crs, extent):
    dest_crs = QgsProject.instance().crs()
    xform = QgsCoordinateTransform(source_crs,
                                dest_crs, 
                                QgsProject.instance().transformContext())
    canvas.setExtent(xform.transform(extent))
    canvas.refresh()

    # print("zoom to", source_crs, extent)

def pos_to_lonlat(pos):
    point = canvas.getCoordinateTransform().toMapCoordinates(pos.x(), pos.y())

    scrs = QgsProject.instance().crs()
    epsg4326 = QgsCoordinateReferenceSystem('EPSG:4326')
    xform = QgsCoordinateTransform(scrs,
                                epsg4326, 
                                QgsProject.instance().transformContext())
    return xform.transform(point)


def pos_to_col_row(layer,pos):
    extent = layer.dataProvider().extent()
    xres = extent.width() / layer.dataProvider().xSize()
    yres = extent.height() / layer.dataProvider().ySize()
    point = canvas.getCoordinateTransform().toMapCoordinates(pos.x(), pos.y())
    x = point[0]
    y = point[1]
            
    row = int(math.floor((extent.yMaximum() - y) / yres))
    col = int(math.floor((x - extent.xMinimum()) / xres))
    return col, row


def setup_taggable_rivers_layer():
    layers = QgsProject.instance().mapLayersByName('rivers')
    river_source = layers[0]

    if not river_source:
        print("Rivers layer not found")
        exit()


    # rivers = river_source.clone()
    # rivers.setName('rivers with cpoints')
    # Add the copy to the project
    # QgsProject.instance().addMapLayer(rivers)

    transform_and_zoom_extent(river_source.crs(), river_source.extent())


    # Create a memory layer instead of cloning
    rivers = QgsVectorLayer("LineString?crs=" + river_source.crs().authid(), 
                        'rivers with cpoints', 
                        "memory")

    # Copy features from source to memory layer
    rivers.startEditing()
    rivers.dataProvider().addAttributes(river_source.fields())
    rivers.updateFields()
    rivers.dataProvider().addFeatures(river_source.getFeatures())
    rivers.commitChanges()

    # update style to set line width to 0.860000
    symbol = rivers.renderer().symbol()
    symbol.setWidth(0.860000)
    rivers.triggerRepaint()

    # Add the temporary layer to the project
    QgsProject.instance().addMapLayer(rivers)



    fields = rivers.fields()
    provider = rivers.dataProvider()

    new_fields = []
    if 'catchment_lat' not in fields.names():
        new_fields.append(QgsField('catchment_lat', QVariant.Double, 'double', 10, 6))
    if 'catchment_lon' not in fields.names():
        new_fields.append(QgsField('catchment_lon', QVariant.Double, 'double', 10, 6))

    # create col and row integer fields
    if 'catchment_col' not in fields.names():
        new_fields.append(QgsField('catchment_col', QVariant.Int, 'integer'))
    if 'catchment_row' not in fields.names():
        new_fields.append(QgsField('catchment_row', QVariant.Int, 'integer'))

    if new_fields:
        provider.addAttributes(new_fields)
        rivers.updateFields()

    return rivers 