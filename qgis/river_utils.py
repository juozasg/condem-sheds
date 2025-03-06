from qgis.core import QgsProject, QgsCoordinateTransform, QgsField
from qgis.PyQt.QtCore import QVariant

def setup_taggable_rivers_layer():
    layers = QgsProject.instance().mapLayersByName('rivers')
    river_source = layers[0]

    if not river_source:
        print("Rivers layer not found")
        exit()

    dest_crs = QgsProject.instance().crs()
    xform = QgsCoordinateTransform(river_source.crs(),
                                dest_crs, 
                                QgsProject.instance().transformContext())
    canvas.setExtent(xform.transform(river_source.extent()))
    canvas.refresh()

    # rivers = river_source.clone()
    # rivers.setName('rivers with cpoints')
    # Add the copy to the project
    # QgsProject.instance().addMapLayer(rivers)


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

    if new_fields:
        provider.addAttributes(new_fields)
        rivers.updateFields()

    return rivers 