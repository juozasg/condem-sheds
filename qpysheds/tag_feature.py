def tag_selected_feature(iface):
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