# Form implementation generated from reading ui file 'MainWindow_NPS.ui'
#
# Created by: PyQt6 UI code generator 6.2.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(780, 700)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.imageLabel = QtWidgets.QLabel(self.centralwidget)
        self.imageLabel.setGeometry(QtCore.QRect(20, 70, 512, 512))
        self.imageLabel.setTextFormat(QtCore.Qt.TextFormat.AutoText)
        self.imageLabel.setObjectName("imageLabel")
        self.horizontalSlider = QtWidgets.QSlider(self.centralwidget)
        self.horizontalSlider.setGeometry(QtCore.QRect(20, 640, 512, 22))
        self.horizontalSlider.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.imageNameLabel = QtWidgets.QLabel(self.centralwidget)
        self.imageNameLabel.setGeometry(QtCore.QRect(20, 610, 451, 20))
        self.imageNameLabel.setObjectName("imageNameLabel")
        self.labelCoordinates = QtWidgets.QLabel(self.centralwidget)
        self.labelCoordinates.setGeometry(QtCore.QRect(20, 10, 451, 20))
        self.labelCoordinates.setObjectName("labelCoordinates")
        self.radioButtonManualRectangle = QtWidgets.QRadioButton(self.centralwidget)
        self.radioButtonManualRectangle.setGeometry(QtCore.QRect(550, 100, 191, 20))
        self.radioButtonManualRectangle.setObjectName("radioButtonManualRectangle")
        self.radioButtonRectangleArray = QtWidgets.QRadioButton(self.centralwidget)
        self.radioButtonRectangleArray.setGeometry(QtCore.QRect(550, 140, 191, 20))
        self.radioButtonRectangleArray.setObjectName("radioButtonRectangleArray")
        self.radioButtonFixedSizRect = QtWidgets.QRadioButton(self.centralwidget)
        self.radioButtonFixedSizRect.setGeometry(QtCore.QRect(550, 180, 191, 20))
        self.radioButtonFixedSizRect.setObjectName("radioButtonFixedSizRect")
        self.radioButtonWholeImage = QtWidgets.QRadioButton(self.centralwidget)
        self.radioButtonWholeImage.setGeometry(QtCore.QRect(550, 220, 191, 20))
        self.radioButtonWholeImage.setObjectName("radioButtonWholeImage")
        self.imageNameLabel_3 = QtWidgets.QLabel(self.centralwidget)
        self.imageNameLabel_3.setGeometry(QtCore.QRect(550, 60, 171, 20))
        self.imageNameLabel_3.setObjectName("imageNameLabel_3")
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(560, 570, 211, 23))
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.pushButtonErase = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonErase.setGeometry(QtCore.QRect(550, 280, 181, 24))
        self.pushButtonErase.setObjectName("pushButtonErase")
        self.pushButtonSave = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonSave.setGeometry(QtCore.QRect(550, 320, 181, 24))
        self.pushButtonSave.setObjectName("pushButtonSave")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(560, 540, 201, 16))
        self.label.setObjectName("label")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 780, 22))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionSelect_folder = QtGui.QAction(MainWindow)
        self.actionSelect_folder.setObjectName("actionSelect_folder")
        self.actionSelect_separate_image = QtGui.QAction(MainWindow)
        self.actionSelect_separate_image.setObjectName("actionSelect_separate_image")
        self.actionQuit = QtGui.QAction(MainWindow)
        self.actionQuit.setObjectName("actionQuit")
        self.menuFile.addAction(self.actionSelect_folder)
        self.menuFile.addAction(self.actionSelect_separate_image)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionQuit)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.imageLabel.setText(_translate("MainWindow", "The images will be displayed here"))
        self.imageNameLabel.setText(_translate("MainWindow", "imageName: "))
        self.labelCoordinates.setText(_translate("MainWindow", "pointer coordinates"))
        self.radioButtonManualRectangle.setText(_translate("MainWindow", "manual rectangle selector"))
        self.radioButtonRectangleArray.setText(_translate("MainWindow", "rectangle array"))
        self.radioButtonFixedSizRect.setText(_translate("MainWindow", "fixed size rectangle"))
        self.radioButtonWholeImage.setText(_translate("MainWindow", "whole image as ROI"))
        self.imageNameLabel_3.setText(_translate("MainWindow", "ROI selection tool"))
        self.pushButtonErase.setText(_translate("MainWindow", "erase last ROI"))
        self.pushButtonSave.setText(_translate("MainWindow", "create resulting xlsx"))
        self.label.setText(_translate("MainWindow", "processLabel"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionSelect_folder.setText(_translate("MainWindow", "Select folder"))
        self.actionSelect_separate_image.setText(_translate("MainWindow", "Select separate image"))
        self.actionQuit.setText(_translate("MainWindow", "Quit"))
