import mido
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon
from qgis.utils import iface
import os


def open_midi_input_port(port_name):
    try:
        input_port: mido.ports.BaseInput = mido.open_input(port_name)  # type: ignore
        print(f"Opened MIDI input port: {port_name}")
        return input_port
    except Exception as e:
        print(f"Error opening MIDI input port: {e}")
        return None


# in_port_name =
input_port = None

def input_loop():
    global input_port
    for message in input_port:
        print(message)


class MidiInputThread(QThread):
    """Thread to handle MIDI input without blocking QGIS"""

    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.running = False

    def run(self):
        self.running = True
        global input_port
        input_port = open_midi_input_port("KeyLab mkII 61:KeyLab mkII 61 MIDI 32:0")

        while self.running and input_port:
            try:
                for message in input_port:
                    if not self.running:
                        break
                    if message.type == 'note_on':
                        note_on(message.note)
                        # print(f"Note {message.note} on")
                    # Process MIDI message here
            except Exception as e:
                print(f"Error in MIDI thread: {e}")
                break

    def stop(self):
        self.running = False
        if input_port:
            input_port.close()

def note_on(note):
    print(note)
    if note == 36:
        previous_feature()
    elif note == 37:
        next_feature()
    elif note == 38:
        zoom_line_start()
    elif note == 39:
        zoom_line_end()
    elif note == 40:
        zoom_selected_feature()


# Global reference to thread and action
midi_thread = None
midi_action = None



def toggle_midi_input(checked):
    """Toggle MIDI input when button is clicked"""
    global midi_thread, input_port
    print("toggle midi input", checked)

    if checked:
        # Create and start thread
        midi_thread = MidiInputThread()
        midi_thread.start()
        print("MIDI input activated")
    else:
        # Button is unchecked, stop MIDI input
        if midi_thread and midi_thread.isRunning():
            midi_thread.stop()
            midi_thread = None
        print("MIDI input deactivated")






def next_feature():
    """
    Select the next feature in the currently selected layer.
    - If no features are selected, selects the first feature
    - If multiple features are selected, uses the last selected one
    - If the layer is a raster layer or has no features, does nothing
    """
    # Get the current layer
    layer = iface.activeLayer()
    if not layer:
        print("No active layer")
        return

    # Check if it's a vector layer
    if layer.type() != 0:  # 0 is QgsMapLayer.VectorLayer
        print("Active layer is not a vector layer")
        return

    # Get the next feature ID
    next_id = get_next_feature_id(layer)
    if next_id is None:
        print("No features available to select")
        return

    # Select the feature
    select_feature_by_id(layer, next_id)
    print(f"Selected next feature with ID: {next_id}")



def previous_feature():
    pass


def get_next_feature_id(layer):
    """
    Find the ID of the next feature to select based on current selection.

    Args:
        layer: The QGIS vector layer to work with

    Returns:
        The feature ID of the next feature to select, or None if no suitable feature
    """
    # Check if layer is valid and is a vector layer
    if not layer or layer.type() != 0:  # 0 is QgsMapLayer.VectorLayer
        return None

    # Get total feature count
    feature_count = layer.featureCount()
    if feature_count == 0:
        return None

    # Get currently selected features
    selected_features = layer.selectedFeatures()

    if not selected_features:
        # No selection - return the first feature ID
        for feature in layer.getFeatures():
            return feature.id()  # Return the ID of the first feature
    else:
        # Get the last selected feature
        current_feature = selected_features[-1]
        current_id = current_feature.id()

        # Find the next feature ID
        found_current = False
        first_id = None

        # Loop through all features to find the next one
        for feature in layer.getFeatures():
            feature_id = feature.id()

            # Remember the first feature ID for wrapping around
            if first_id is None:
                first_id = feature_id

            # If we found the current feature, the next one is what we want
            if found_current:
                return feature_id

            # Mark when we find the current feature
            if feature_id == current_id:
                found_current = True

        # If we've reached here, we need to wrap around to the first feature
        return first_id


def select_feature_by_id(layer, feature_id):
    """
    Select a feature in the given layer by its ID.

    Args:
        layer: The QGIS vector layer containing the feature
        feature_id: The ID of the feature to select
    """
    if not layer or layer.type() != 0 or feature_id is None:
        return

    # Clear current selection
    layer.removeSelection()

    # Select the feature
    layer.select(feature_id)

    # Optionally zoom to the selected feature
    iface.mapCanvas().zoomToSelected(layer)

# Create action
midi_action = QAction("MIDI", iface.mainWindow())
midi_action.setCheckable(True)

# Try to load an icon if available (optional)
plugin_dir = os.path.dirname(__file__)
icon_path = os.path.join(plugin_dir, 'icons', 'midi.png')
if os.path.exists(icon_path):
    midi_action.setIcon(QIcon(icon_path))

# Connect toggle event
midi_action.toggled.connect(toggle_midi_input)

# Add to toolbar
print("add toolbar MIDI")
toolbar = iface.addToolBar("MIDI Control")
toolbar.addAction(midi_action)









