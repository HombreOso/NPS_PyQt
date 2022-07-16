import PyQt6
from MainWindow_NPS import Ui_MainWindow

import random
import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow

from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qtagg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

class MainWindow(QMainWindow, Ui_MainWindow):
   def __init__(self):
       super().__init__()
       self.setupUi(self)
       self.show()
       # You can still override values from your UI file within yourcode,
       # but if possible, set them in Qt Creator. See the propertiespanel.
       f = self.label.font()
       f.setPointSize(25)
       self.label.setAlignment(
           Qt.AlignmentFlag.AlignHCenter
           | Qt.AlignmentFlag.AlignVCenter
       )
       self.label.setFont(f)
       # Signals from UI widgets can be connected as normal.
       self.pushButton.pressed.connect(self.update_label)
   def update_label(self):
       n = random.randint(1, 6)
       self.label.setText("%d" % n)
app = QApplication(sys.argv)
w = MainWindow()
app.exec()