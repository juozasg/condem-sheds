import time
import mido
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon
from qgis.utils import iface
from qgis.core import QgsTask, QgsApplication
import os


def open_midi_input_port(port_name):
    try:
        input_port: mido.ports.BaseInput = mido.open_input(port_name)  # type: ignore
        print(f"Opened MIDI input port: {port_name}")
        return input_port
    except Exception as e:
        print(f"Error opening MIDI input port: {e}")
        return None


running = False

def input_loop(task, wait_time):
    # global input_port
    # print("input loop")
    QgsMessageLog.logMessage("input loop TASK")
    # return {'note': 'fuuck'}
    input_port = open_midi_input_port("KeyLab mkII 61:KeyLab mkII 61 MIDI 32:0")
    QgsMessageLog.logMessage("opened input port")
    for message in input_port:
        QgsMessageLog.logMessage("message")
        if message.type == 'note_on':
            QgsMessageLog.logMessage("note on")
            QgsMessageLog.logMessage("closing input port")
            input_port.close()
            return {'note': message.note, task: task}


def note_received(exception, result):
    print("note received", exception, result)
    if not exception:
        try:
            note_on(result['note'])
        finally:
            start_task()


def start_task():
    global running
    # print("running?", running)
    if not running:
        return

    task = QgsTask.fromFunction("MIDI Input 1", input_loop, on_finished=note_received, wait_time=5)
    QgsApplication.taskManager().addTask(task)
    print("added task")


def start():
    global running
    running = True
    start_task()

def stop():
    global running
    running = False


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
        start()
        # print("MIDI input activated")
    else:
        # Button is unchecked, stop MIDI input
        stop()
        # print("MIDI input deactivated"



def next_feature(previous=False):
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
    select_id = get_next_feature_id(layer, previous=previous)
    if select_id is None:
        print("No features available to select")
        return

    # Select the feature
    select_feature_by_id(layer, select_id)
    print(f"Selected next feature with ID: {select_id}")



def previous_feature():
    next_feature(previous=True)


def get_next_feature_id(layer, previous=False):
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


def select_feature_by_id(layer, feature_id):
    """
    Select a feature in the given layer by its ID.

    Args:
        layer: The QGIS vector layer containing the feature
        feature_id: The ID of the feature to select
    """
    if not layer or layer.type() != 0 or feature_id is None:
        return

    print("selecting feature", feature_id)
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









