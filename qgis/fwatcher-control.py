from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon
from qgis.utils import iface
from qgis.core import QgsTask, QgsApplication
import os

FNAME="file-pipe.txt"


def start():
  pass

def stop():
  pass

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