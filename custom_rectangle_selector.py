from PyQt6.QtWidgets import (
    QWidget, QApplication, QLabel, QVBoxLayout, QHBoxLayout, QMainWindow, QScrollArea,
    QPushButton
)
from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QImage, QPixmap, QPainter, QPen
import cv2, sys
import PIL

from PIL import Image

I_MAX_CROP_IMAGE_WIDTH = 512


class SelectImageTool(QLabel):
    def __init__(self, mStrImageName, mFlScaleFactor):
        super().__init__()
        self.aStrImageName = mStrImageName
        self.iPosX0 = 0
        self.iPosY0 = 0
        self.iPosX1 = 0
        self.iPosY1 = 0
        self.aFlScaleFactor = mFlScaleFactor
        self.blnMousePress = False

    def mousePressEvent(self, event):
        self.blnMousePress = True
        self.iPosX0 = event.position().x()
        self.iPosY0 = event.position().y()

    def mouseReleaseEvent(self, event):
        self.blnMousePress = False

    def mouseMoveEvent(self, event):
        if self.blnMousePress:
            self.iPosX1 = event.position().x()
            self.iPosY1 = event.position().y()
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        rctCropArea = QRect(int(self.iPosX0), int(self.iPosY0),
                            int(abs(self.iPosX1 - self.iPosX0)), int(abs(self.iPosY1 - self.iPosY0)))
        pntSelectionRectangle = QPainter(self)
        pntSelectionRectangle.setPen(QPen(Qt.GlobalColor.red, 4, Qt.PenStyle.DashLine))
        pntSelectionRectangle.drawRect(rctCropArea)

    def setSelectionEdge(self):

        iScalePosX0 = self.scaleCoordinates(self.iPosX0)
        iScalePosX1 = self.scaleCoordinates(self.iPosX1)
        iScalePosY0 = self.scaleCoordinates(self.iPosY0)
        iScalePosY1 = self.scaleCoordinates(self.iPosY1)

        iLeft = iScalePosX0
        iTop = iScalePosY0
        iWidth = abs(iScalePosX1 - iScalePosX0)
        iHeight = abs(iScalePosY1 - iScalePosY0)
        iRight = iLeft + iWidth
        iBottom = iTop + iHeight
        print(str(iLeft) + " " + str(iTop) + " " + str(iRight) + " " + str(iBottom))

        return iLeft, iTop, iRight, iBottom

    def scaleCoordinates(self, mIntCoordinate):

        return round(self.aFlScaleFactor * mIntCoordinate)

    def cropImageSelection(self):

        iLeft, iTop, iRight, iBottom = self.setSelectionEdge()

        try:
            imgSourcePicture = Image.open(self.aStrImageName)

            # prevent rotating the jpeg image
            imgSourcePicture = PIL.ImageOps.exif_transpose(imgSourcePicture)

            tupSize = imgSourcePicture.size

            iLeft = self.checkCoordinateLimit(iLeft, 0)
            iTop = self.checkCoordinateLimit(iTop, 0)
            iRight = self.checkCoordinateLimit(iRight, tupSize[0])
            iBottom = self.checkCoordinateLimit(iBottom, tupSize[1])

            imgCropped = imgSourcePicture.crop((iLeft, iTop, iRight, iBottom))

            imgCropped.save("cropped.jpg")

        except IOError:
            pass

    def checkCoordinateLimit(self, mIntCoord, mIntLimit):

        if mIntLimit == 0:
            iCoord = mIntCoord if mIntCoord >= mIntLimit else mIntLimit
        else:
            iCoord = mIntCoord if mIntCoord <= mIntLimit else mIntLimit

        return iCoord


class ImageCropperBox(QMainWindow):
    def __init__(self):
        super().__init__()

        self.resize(600, 700)
        self.setWindowTitle('Seleziona la parte dell\'immagine da salvare')

        strImgName = "1.jpg"
        imgSourceImage = cv2.imread(strImgName)
        pxmSourceImage, iWidth, iHeight = self.createPixMap(imgSourceImage)

        if iWidth > I_MAX_CROP_IMAGE_WIDTH:
            pxmSourceImage = pxmSourceImage.scaledToWidth(I_MAX_CROP_IMAGE_WIDTH)
            flScaleFactor = round(iWidth / I_MAX_CROP_IMAGE_WIDTH, 2)
        else:
            flScaleFactor = 1

        self.sitImageLabel = SelectImageTool(strImgName, flScaleFactor)
        self.sitImageLabel.setStyleSheet("background:navy")
        self.sitImageLabel.setFixedSize(pxmSourceImage.width(), pxmSourceImage.height())
        self.sitImageLabel.setPixmap(pxmSourceImage)
        self.sitImageLabel.setCursor(Qt.CursorShape.CrossCursor)

        widImagePanel = QWidget()
        layvImagePanel = QVBoxLayout()
        saImagePanel = QScrollArea()

        widImgBox = QWidget()
        layvImgBox = QVBoxLayout()

        widButtonBox = QWidget()
        layhButtonBox = QHBoxLayout()

        widImgBox.setLayout(layvImgBox)

        widButtonBox.setLayout(layhButtonBox)

        butSave = QPushButton("Salva l'immagine")
        butDelete = QPushButton("Elimina l'immagine")

        butSave.clicked.connect(lambda state: self.saveImageSelection(self.sitImageLabel))

        layhButtonBox.addWidget(butSave)
        layhButtonBox.addWidget(butDelete)

        widImagePanel.setLayout(layvImagePanel)
        saImagePanel.setWidget(widImagePanel)
        self.setScrollAreaProperties(saImagePanel)

        layvImagePanel.addWidget(widImgBox)
        layvImagePanel.addWidget(widButtonBox)

        layvImgBox.addWidget(self.sitImageLabel)
        self.setCentralWidget(saImagePanel)

    def setScrollAreaProperties(self, saImgBox):
        saImgBox.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        saImgBox.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        saImgBox.setWidgetResizable(True)

    def createPixMap(self, imgSourceImage):

        iHeight, iWidth, bytesPerComponent = imgSourceImage.shape
        bytesPerLine = 3 * iWidth
        cv2.cvtColor(imgSourceImage, cv2.COLOR_BGR2RGB, imgSourceImage)
        QImg = QImage(imgSourceImage.data, iWidth, iHeight, bytesPerLine, QImage.Format.Format_RGB888)
        pxmSourceImage = QPixmap.fromImage(QImg)

        return pxmSourceImage, iWidth, iHeight

    def saveImageSelection(self, msitImageLabel):
        msitImageLabel.cropImageSelection()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    icbMain = ImageCropperBox()
    icbMain.show()
    app.exec()