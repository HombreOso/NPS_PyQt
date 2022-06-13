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
    width: 800
    height: 800

    color: Constants.backgroundColor

    Text {
        text: qsTr("Hello MainWindow_NPS")
        anchors.centerIn: parent
        font.family: Constants.font.family
    }

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
        id: radioButton
        x: 531
        y: 62
        width: 134
        height: 24
        text: qsTr("manual rectangle")
    }

    RadioButton {
        id: radioButton1
        x: 531
        y: 92
        width: 134
        height: 24
        text: qsTr("fixed size rectangle")
    }

    RadioButton {
        id: radioButton2
        x: 531
        y: 122
        width: 134
        height: 24
        text: qsTr("rectangle array")
    }

    Label {
        id: label2
        x: 531
        y: 40
        width: 134
        height: 16
        text: qsTr("ROI selection tool")
    }
}
