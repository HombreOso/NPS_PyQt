/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/

import QtQuick
import QtQuick.Controls
import MainWindow_NPS

Rectangle {
    id: rectangle
    width: 700
    height: 630
    color: "#cfcfcf"
    property alias progressBar: progressBar
    property alias coordinates_label1: coordinates_label1
    property alias saveButton: saveButton
    property alias eraseButton: eraseButton
    property alias roiSelectionTool: roiSelectionTool
    property alias wholeImagerb: wholeImagerb
    property alias rectangleArrayrb: rectangleArrayrb
    property alias fixedSizeRectanglerb: fixedSizeRectanglerb
    property alias manualRectanglerb: manualRectanglerb
    property alias coordinates_label: coordinates_label
    property alias slider: slider
    property alias sliding_images_label: sliding_images_label


    Label {
        id: sliding_images_label
        x: 8
        y: 62
        width: 512
        height: 512
        text: qsTr("Label")
    }

    Slider {
        id: slider
        x: 8
        y: 580
        width: 512
        height: 50
        wheelEnabled: true
        value: 0.5
    }

    Label {
        id: coordinates_label
        x: 8
        y: 40
        width: 512
        text: qsTr("Label")
    }

    RadioButton {
        id: manualRectanglerb
        x: 531
        y: 62
        width: 134
        height: 24
        text: qsTr("manual rectangle")
    }

    RadioButton {
        id: fixedSizeRectanglerb
        x: 531
        y: 92
        width: 134
        height: 24
        text: qsTr("fixed size rectangle")
    }

    RadioButton {
        id: rectangleArrayrb
        x: 531
        y: 122
        width: 134
        height: 24
        text: qsTr("rectangle array")
    }

    RadioButton {
        id: wholeImagerb
        x: 531
        y: 152
        width: 134
        height: 24
        text: qsTr("whole image")
    }

    Label {
        id: roiSelectionTool
        x: 531
        y: 40
        width: 134
        height: 16
        text: qsTr("ROI selection tool")
    }


    Button {
        id: eraseButton
        x: 531
        y: 182
        width: 93
        height: 30
        text: qsTr("Erase last ROI")
    }

    Button {
        id: saveButton
        x: 531
        y: 218
        width: 134
        height: 30
        text: qsTr("Save ROIs -> create xlsx")
    }

    Label {
        id: coordinates_label1
        x: 8
        y: 8
        width: 512
        color: "#000000"
        text: qsTr("NPS assessment tool")
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        font.italic: true
        font.weight: Font.Normal
    }

    ProgressBar {
        id: progressBar
        x: 480
        y: 389
        width: 320
        height: 50
        transformOrigin: Item.Center
        clip: false
        rotation: 90
        value: 0.5
    }
}
