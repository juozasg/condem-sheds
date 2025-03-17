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


def note_on(code):
    if code == 36:
        previous_feature()
    elif code == 37:
        next_feature()
    elif code == 38:
        zoom_line_start()
    elif code == 39:
        zoom_line_end()
    elif code == 40:
        zoom_selected_feature()


# Global reference to thread and action
midi_thread = None
midi_action = None




