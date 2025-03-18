from PyQt5.QtCore import Qt, QThread, pyqtSignal, QFileSystemWatcher
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon
from qgis.utils import iface
from qgis.core import QgsTask, QgsApplication
import os
import mido



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


def zoom_selected_feature():
    layer = iface.activeLayer()
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
    iface.mapCanvas().zoomToSelected(layer)
    # print("Zoomed to selected feature(s)")
    iface.mapCanvas().zoomByFactor(1.5)


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
    # return
    # Clear current selection
    layer.removeSelection()

    # Select the feature
    layer.select(feature_id)

    # Optionally zoom to the selected feature
    iface.mapCanvas().zoomToSelected(layer)

    # zoom out by 10%
    iface.mapCanvas().zoomByFactor(1.25)


    # show notification with feature id and name attribute
    feature = layer.getFeature(feature_id)
    if feature:
        name = feature.attribute("name")
        iface.messageBar().pushMessage(
            "Feature Selected",
            f"ID: {feature_id}, Name: {name}",
            level=Qgis.Info,
            duration=5,
        )
        # identify the feature with identify tool
        iface.actionIdentify().trigger()




def zoom_line(start=True):
    """
    Zoom to the first or last vertex of the currently selected LineString feature.

    Args:
        start (bool): If True, zoom to the first vertex. If False, zoom to the last vertex.
    """
    layer = iface.activeLayer()
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

    if not geometry or not geometry.isMultipart() and geometry.type() != 1:  # 1 is LineString
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
    iface.mapCanvas().setCenter(QgsPointXY(vertex))
    iface.mapCanvas().zoomScale(1200)  # Set fixed scale to 1:1500
    print(f"Zoomed to {'start' if start else 'end'} vertex: {vertex}")

def proccess(code):
    print("code = ", code)
    if code == 36:
        previous_feature()
    elif code == 37:
        next_feature()
    elif code == 38:
        zoom_line(True)
    elif code == 39:
        zoom_line(False)
    elif code == 40:
        zoom_selected_feature()



#### CONTROL CODE

FNAME="midi-pipe"
FPATH = os.path.join(os.path.dirname(__file__), FNAME)

class MidiInputThread(QThread):
    """Thread to handle MIDI input without blocking QGIS"""

    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.running = False
        self.input_port = None

    def run(self):
        self.running = True
        self.input_port = mido.open_input("KeyLab mkII 61:KeyLab mkII 61 MIDI 36:0")

        while self.running and self.input_port:
            try:
                for message in self.input_port:
                    if not self.running:
                        break
                    if message.type == 'note_on':
                        with open(FPATH, 'w') as file:
                            file.write(str(message.note))
                        # print(f"Note {message.note} on")
                    # Process MIDI message here
            except Exception as e:
                # print(f"Error in MIDI thread: {e}")
                break

    def stop(self):
        self.running = False
        if self.input_port:
            self.input_port.close()

midi_thread = None

watcher = None  # Global variable to hold the QFileSystemWatcher instance

def on_file_changed(path):
    try:
        with open(path, 'r+') as file:
            contents = file.read()
            # if contents is an integer call proccess(code)
            try:
                proccess(int(contents))
            except Exception as e:
                print("Error processing code: ", e)
            finally:
                watcher.removePath(FPATH)
                file.truncate(0)  # Clear file contents
            watcher.addPath(FPATH)
    except Exception as e:
        print(f"Error reading or clearing file: {e}")

def start():
    global watcher, midi_thread
    if midi_thread is None:
        midi_thread = MidiInputThread()
        midi_thread.start()
        print("Started MIDI input thread")
    if watcher is None:
        watcher = QFileSystemWatcher()
        watcher.fileChanged.connect(on_file_changed)
        watcher.addPath(FPATH)
        print(f"Started watching {FPATH}")

def stop():
    global watcher, midi_thread
    if midi_thread is not None:
        midi_thread.stop()
        midi_thread = None
        print("Stopped MIDI input thread")
    if watcher is not None:
        watcher.fileChanged.disconnect(on_file_changed)
        watcher.removePath(FPATH)
        watcher = None
        print(f"Stopped watching {FPATH}")

def enable_file_pipe(checked):
		if checked:
			print("File pipe enabled")
			# Start file pipe
			start()
		else:
			print("File pipe disabled")
			# Stop file pipe
			stop()


# Create action
action = QAction("file-pipe", iface.mainWindow())
action.setCheckable(True)

# Try to load an icon if available (optional)
plugin_dir = os.path.dirname(__file__)
icon_path = os.path.join(plugin_dir, 'icons', 'midi.png')
if os.path.exists(icon_path):
    action.setIcon(QIcon(icon_path))

# Connect toggle event
action.toggled.connect(enable_file_pipe)

# Add to toolbar
toolbar = iface.addToolBar("File Pipe Control")
toolbar.addAction(action)


