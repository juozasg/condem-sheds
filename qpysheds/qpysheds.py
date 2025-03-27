import random
from PyQt5.QtWidgets import QAction, QMessageBox
from qgis.gui import QgisInterface
from qgis.core import *

from qpysheds.tag_feature import tag_selected_feature, toggle_werk_layergroup

from .navigator import Navigator

class QPySheds:
    def __init__(self, iface: QgisInterface):
        self.iface = iface
        self.navigator = Navigator(iface)

    def initGui(self):
        # self.action = QAction('Go!', self.iface.mainWindow())
        # self.action.triggered.connect(self.run)
        # self.iface.addToolBarIcon(self.action)
        # self.action = QAction('YOLO!', self.iface.mainWindow())
        # self.action.triggered.connect(self.run)
        # self.iface.addToolBarIcon(self.action)

        # self.toolbar.addAction(self.action)
        # self.iface.addPluginToMenu("QPySheds", self.action)
        # self.iface.addToolBarIcon(action)

        self.toolbar = self.iface.addToolBar("QPySheds")
        self.actions = []

        # PREV
        action = QAction("Prev", self.iface.mainWindow())
        # action.setText("Select Previous Feature")
        action.triggered.connect(self.navigator.previous_feature)
        self.iface.registerMainWindowAction(action, 'Ф')
        self.iface.addPluginToMenu("QPySheds", action)
        self.toolbar.addAction(action)
        self.actions.append(action)

        # NEXT
        action = QAction("Next", self.iface.mainWindow())
        # action.setText("Select Next Feature")
        action.triggered.connect(self.navigator.next_feature)
        self.iface.registerMainWindowAction(action, 'В')
        self.iface.addPluginToMenu("QPySheds", action)
        self.toolbar.addAction(action)
        self.actions.append(action)

        # LINE START
        action = QAction("L-start", self.iface.mainWindow())
        # action.setText("Select Next Feature")
        action.triggered.connect(lambda: self.navigator.zoom_line(True))
        self.iface.registerMainWindowAction(action, 'Й')
        self.iface.addPluginToMenu("QPySheds", action)
        self.toolbar.addAction(action)
        self.actions.append(action)

        # LINE END
        action = QAction("L-end", self.iface.mainWindow())
        action.triggered.connect(lambda: self.navigator.zoom_line(False))
        self.iface.registerMainWindowAction(action, 'У')
        self.iface.addPluginToMenu("QPySheds", action)
        self.toolbar.addAction(action)
        self.actions.append(action)

        # TAG
        action = QAction("Tag", self.iface.mainWindow())
        action.triggered.connect(lambda: tag_selected_feature(self.iface))
        self.iface.registerMainWindowAction(action, 'Е')
        self.iface.addPluginToMenu("QPySheds", action)
        self.toolbar.addAction(action)
        self.actions.append(action)


        # Toggle
        action = QAction("Togl", self.iface.mainWindow())
        action.triggered.connect(lambda: toggle_werk_layergroup(self.iface))
        self.iface.registerMainWindowAction(action, 'Ц')
        self.iface.addPluginToMenu("QPySheds", action)
        # self.toolbar.addAction(action)
        self.actions.append(action)

        # action = QAction("Next", self.iface.mainWindow())
        # action.triggered.connect(self.navigator.next_feature)
        # # self.iface.registerMainWindowAction(action, 'в')
        # self.iface.addPluginToMenu("&QPySheds", action)
        # # self.iface.addPluginToMenu("QPySheds-1", action)
        # self.actions.append(action)

        # action = QAction("L-start", self.iface.mainWindow())
        # action.triggered.connect(lambda: self.navigator.zoom_line(True))
        # self.actions.append(action)

        # action = QAction("L-end", self.iface.mainWindow())
        # action.triggered.connect(lambda: self.navigator.zoom_line(False))
        # self.actions.append(action)



        # copy_action = QAction("Copy to Tagged")
        # copy_action.triggered.connect(copy_to_tagged)

        # label = QLabel("ID:")
        # text_id = QLineEdit()
        # text_id.setMaximumSize(QSize(40, 100))
        # text_id.setText('0')

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu("QPySheds", action)
            # self.iface.removeToolBarIcon(action)
            self.toolbar.removeAction(action)
        del self.actions
        del self.toolbar

    def run(self):
        QMessageBox.information(None, 'Plugin - ' + str(random.random()), 'werk werk werk werk werk werk')


# Try to load an icon if available (optional)
# plugin_dir = os.path.dirname(__file__)
# icon_path = os.path.join(plugin_dir, 'icons', 'midi.png')
# if os.path.exists(icon_path):
#     action.setIcon(QIcon(icon_path))