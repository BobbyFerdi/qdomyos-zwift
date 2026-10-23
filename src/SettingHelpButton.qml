import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls.Material 2.15

// A small "?" button for a setting: tapping it opens a popup with the description of the setting.
// It sits inline right after the title of the setting (see tools/restyle_settings.py).
Button {
    id: root

    property string helpText: ""

    visible: helpText !== ""
    implicitWidth: 28
    implicitHeight: 28
    padding: 0
    topInset: 0
    bottomInset: 0
    leftInset: 0
    rightInset: 0
    flat: true
    text: "?"
    font.bold: true
    font.pixelSize: 14
    Material.foreground: "#B388FF"

    background: Rectangle {
        radius: width / 2
        color: helpPopup.opened ? Qt.rgba(0.49, 0.30, 1.0, 0.30) : "transparent"
        border.width: 1
        border.color: Qt.rgba(0.70, 0.53, 1.0, 0.55)
    }

    onClicked: helpPopup.open()

    Accessible.role: Accessible.Button
    Accessible.name: qsTr("Help")
    Accessible.description: qsTr("Show the description of this setting")

    Popup {
        id: helpPopup
        parent: Overlay.overlay
        anchors.centerIn: Overlay.overlay
        modal: true
        width: Math.min(Overlay.overlay ? Overlay.overlay.width - 48 : 320, 420)
        padding: 20
        closePolicy: Popup.CloseOnPressOutside | Popup.CloseOnEscape

        background: Rectangle {
            radius: 16
            color: Qt.lighter(Material.backgroundColor, 1.3)
            border.width: 1
            border.color: Qt.rgba(0.70, 0.53, 1.0, 0.55)
        }

        contentItem: Label {
            text: root.helpText
            wrapMode: Text.WordWrap
            textFormat: Text.PlainText
            color: "#d0d0da"
        }
    }
}
