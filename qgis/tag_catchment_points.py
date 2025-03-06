rivers_layer = None
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

rivers = river_source.clone()
rivers.setName('rivers with cpoints')
# Add the copy to the project
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