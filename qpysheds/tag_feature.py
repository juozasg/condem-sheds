from qgis.core import QgsProject, QgsFeature, QgsMapLayer

def tag_selected_feature(iface):
    # Check if the tagged layer exists
    tagged_layer = QgsProject.instance().mapLayersByName('tagged')
    if not tagged_layer:
        iface.messageBar().pushMessage("Error", "Layer 'tagged' not found", level=1)
        return

    tagged_layer = tagged_layer[0]

    layer = iface.activeLayer()
    if not layer or layer.type() != 0:  # 0 is QgsMapLayer.VectorLayer
        return

    # Get the selected features
    selected_features = layer.selectedFeatures()
    if not selected_features:
        return

    for feature in selected_features:
        # Create a new feature with the same geometry
        new_feature = QgsFeature(tagged_layer.fields())
        new_feature.setGeometry(feature.geometry())

        # add field names if missing
        for field in layer.fields():
            if tagged_layer.fields().indexOf(field.name()) < 0:
                tagged_layer.dataProvider().addAttributes([field])

        # Copy attributes if field names match
        for field_name in layer.fields().names():
            if tagged_layer.fields().indexOf(field_name) >= 0:
                new_feature[field_name] = feature[field_name]

        # Add the feature to the tagged layer
        # handle errors

        tagged_layer.startEditing()
        tagged_layer.addFeature(new_feature)
        success = tagged_layer.commitChanges()

        if not success:
            iface.messageBar().pushMessage("Error", "Failed to copy feature", level=1)
            print(tagged_layer.commitErrors())
            tagged_layer.rollBack()
            return


        iface.messageBar().pushMessage("Success", "Feature copied to 'tagged' layer", level=3, duration=1)

def toggle_werk_layergroup(iface):
    # Check if the tagged layer exists
    werk_layergroup = QgsProject.instance().layerTreeRoot().findGroup('werk')
    if not werk_layergroup:
        iface.messageBar().pushMessage("Error", "Layer group 'werk' not found", level=1)
        return

    # werk_layergroup = werk_layergroup.layer()

    if werk_layergroup.isVisible():
        werk_layergroup.setItemVisibilityChecked(False)
    else:
        werk_layergroup.setItemVisibilityChecked(True)