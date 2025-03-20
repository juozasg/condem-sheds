import qgis
from qgis.core import Qgis

from PyQt5.QtCore import Qt


class Navigator:
    def __init__(self, iface):
        self.iface = iface

    def next_feature(self, previous=False):
        """
        Select the next feature in the currently selected layer.
        - If no features are selected, selects the first feature
        - If multiple features are selected, uses the last selected one
        - If the layer is a raster layer or has no features, does nothing
        """
        # Get the current layer
        layer = self.iface.activeLayer()
        if not layer:
            print("No active layer")
            return

        # Check if it's a vector layer
        if layer.type() != 0:  # 0 is QgsMapLayer.VectorLayer
            print("Active layer is not a vector layer")
            return

        # Get the next feature ID
        select_id = self.get_next_feature_id(layer, previous=previous)
        if select_id is None:
            print("No features available to select")
            return

        # Select the feature
        self.select_feature_by_id(layer, select_id)
        print(f"Selected next feature with ID: {select_id}")

    def previous_feature(self):
        self.next_feature(previous=True)

    def zoom_selected_feature(self):
        layer = self.iface.activeLayer()
        if not layer:
            return

        # Check if it's a vector layer
        if layer.type() != 0:  # 0 is QgsMapLayer.VectorLayer
            return

        # Get the selected features
        selected_features = layer.selectedFeatures()
        if not selected_features:
            return

        # Zoom to the selected features
        self.iface.mapCanvas().zoomToSelected(layer)
        self.iface.mapCanvas().zoomByFactor(1.5)

    def get_next_feature_id(self, layer, previous=False):
        """
        Find the ID of the next/previous feature to select based on current selection.

        Args:
            layer: The QGIS vector layer to work with
            previous: If True, select previous feature instead of next (default: False)

        Returns:
            The feature ID of the next/previous feature to select, or None if no suitable feature
        """
        # Check if layer is valid and is a vector layer
        if not layer or layer.type() != 0:  # 0 is QgsMapLayer.VectorLayer
            return None

        # Get total feature count
        feature_count = layer.featureCount()
        if feature_count == 0:
            return None

        # Build a list of feature IDs
        feature_ids = [f.id() for f in layer.getFeatures()]
        if not feature_ids:
            return None

        # Get currently selected features
        selected_features = layer.selectedFeatures()

        if not selected_features:
            # No selection - return first or last ID depending on direction
            return feature_ids[-1 if previous else 0]
        else:
            # Get the last selected feature
            current_id = selected_features[-1].id()

            # Find current feature's index in the list
            try:
                current_index = feature_ids.index(current_id)
            except ValueError:
                # If current ID isn't found, start from beginning/end
                return feature_ids[-1 if previous else 0]

            # Calculate next/previous index with wrapping
            if previous:
                next_index = (current_index - 1) % len(feature_ids)
            else:
                next_index = (current_index + 1) % len(feature_ids)

            return feature_ids[next_index]

    def select_feature_by_id(self, layer, feature_id):
        """
        Select a feature in the given layer by its ID.

        Args:
            layer: The QGIS vector layer containing the feature
            feature_id: The ID of the feature to select
        """
        if not layer or layer.type() != 0 or feature_id is None:
            return

        print("selecting feature", feature_id)
        # Clear current selection
        layer.removeSelection()

        # Select the feature
        layer.select(feature_id)

        # Optionally zoom to the selected feature
        self.iface.mapCanvas().zoomToSelected(layer)

        # Zoom out by 10%
        self.iface.mapCanvas().zoomByFactor(1.25)

        # Show notification with feature ID and name attribute
        feature = layer.getFeature(feature_id)
        if feature:
            name = feature.attribute("name")
            self.iface.messageBar().pushMessage(
                f"Selected: {feature_id} ({name})",
                level=Qgis.Info,
                duration=3,
            )
            # Trigger the identify tool
            self.iface.actionIdentify().trigger()

    def zoom_line(self, start=True):
        """
        Zoom to the first or last vertex of the currently selected LineString feature.

        Args:
            start (bool): If True, zoom to the first vertex. If False, zoom to the last vertex.
        """
        layer = self.iface.activeLayer()
        if not layer:
            return

        # Check if it's a vector layer
        if layer.type() != 0:  # 0 is QgsMapLayer.VectorLayer
            return

        # Get the selected features
        selected_features = layer.selectedFeatures()
        if not selected_features:
            return

        # Process the first selected feature
        feature = selected_features[0]
        geometry = feature.geometry()

        if (
            not geometry or not geometry.isMultipart() and geometry.type() != 1
        ):  # 1 is LineString
            print("Selected feature is not a LineString")
            return

        # Get the vertices of the LineString
        vertices = list(geometry.vertices())
        if not vertices:
            print("No vertices found in the LineString")
            return

        # Choose the vertex to zoom to
        vertex = vertices[0] if start else vertices[-1]

        # Zoom to the vertex
        self.iface.mapCanvas().setCenter(qgis.core.QgsPointXY(vertex))
        self.iface.mapCanvas().zoomScale(1200)  # Set fixed scale to 1:1500
        print(f"Zoomed to {'start' if start else 'end'} vertex: {vertex}")
