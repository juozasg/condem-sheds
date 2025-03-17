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
                    print(message)
                    # Process MIDI message here
            except Exception as e:
                print(f"Error in MIDI thread: {e}")
                break

    def stop(self):
        self.running = False
        if input_port:
            input_port.close()


# Global reference to thread and action
midi_thread = None
midi_action = None






def toggle_midi_input(checked):
    """Toggle MIDI input when button is clicked"""
    global midi_thread, input_port
    print("toggle midi input", checked)

    if checked:
        # Button is checked, start MIDI input
        # if not input_port:
        #     input_port = open_midi_input_port(in_port_name)
        #     if not input_port:
        #         midi_action.setChecked(False)
        #         return

        # Create and start thread
        midi_thread = MidiInputThread()
        midi_thread.start()
        print("MIDI input activated")
    else:
        # Button is unchecked, stop MIDI input
        if midi_thread and midi_thread.isRunning():
            midi_thread.stop()
            # midi_thread.wait()  # Wait for thread to finish
            midi_thread = None
        print("MIDI input deactivated")


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









