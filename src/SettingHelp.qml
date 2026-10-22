import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Controls.Material 2.15
import QtQuick.Layouts 1.15

// The help for one setting, collapsed to a small "?" button: tapping it shows or hides the description.
// It takes the properties the settings pages already set on the help Label it replaces (see tools/restyle_settings.py).
ColumnLayout {
    id: root

    property alias text: helpLabel.text
    property alias textFormat: helpLabel.textFormat
    property alias wrapMode: helpLabel.wrapMode
    property alias verticalAlignment: helpLabel.verticalAlignment
    property alias color: helpLabel.color
    property alias font: helpLabel.font
    property bool open: false

    spacing: 2
    Layout.fillWidth: true
    // A layout is no wider than its widest child allows, and the lone "?" button caps that at its own width
    Layout.maximumWidth: 100000
    // The "?" row is mostly empty: pull it up under the setting it belongs to and close the gap below
    Layout.topMargin: -8
    Layout.bottomMargin: -4

    Button {
        id: helpButton
        Layout.alignment: Qt.AlignRight
        Layout.preferredWidth: 28
        Layout.preferredHeight: 28
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
            color: root.open ? Qt.rgba(0.49, 0.30, 1.0, 0.30) : "transparent"
            border.width: 1
            border.color: Qt.rgba(0.70, 0.53, 1.0, 0.55)
        }

        onClicked: root.open = !root.open

        Accessible.role: Accessible.Button
        Accessible.name: qsTr("Help")
        Accessible.description: root.open ? qsTr("Hide the description of this setting") : qsTr("Show the description of this setting")
    }

    Label {
        id: helpLabel
        visible: root.open
        Layout.fillWidth: true
        wrapMode: Text.WordWrap
        textFormat: Text.PlainText
        color: "#9a9aa8"
        font.pixelSize: Qt.application.font.pixelSize - 2
    }
}
