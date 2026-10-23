import QtQuick 2.7
import QtQuick.Layouts 1.3
import QtQuick.Controls 2.15
import QtQuick.Controls.Material 2.15
import Qt.labs.settings 1.0

// One tile (or option) of the settings: a card with its title and an on/off switch; the settings of the
// tile show inside the card while the switch is on.
Pane {
    property Settings settings: null
    id: rootElement
    property  bool linkedBoolSettingDefault: false
    property string linkedBoolSetting: "example_setting"
    property bool isOpen: false
    property string title: ""
    property string helpText: ""
    property bool helpOpen: false
    default property alias accordionContent: contentPlaceholder.data

    function convertValue(val) {
        let tpval = typeof(val);
        if (tpval==="undefined") return false;
        else if (tpval==="string") return val === "true";
        else if (tpval==="number") return val !== 0;
        else if (tpval==="boolean") return val;
        else return false;

    }

    Component.onCompleted: function() {
        if (typeof(settings[linkedBoolSetting])=="undefined")
            isOpen = convertValue(settings.value(linkedBoolSetting, linkedBoolSettingDefault));
        else
            isOpen = convertValue(settings[linkedBoolSetting]);
    }

    Layout.fillWidth: true
    Layout.topMargin: 6
    Layout.leftMargin: 8
    Layout.rightMargin: 8
    padding: 0

    background: Rectangle {
        radius: 14
        color: Qt.lighter(Material.backgroundColor, 1.3)
        border.width: 1
        border.color: rootElement.isOpen ? Qt.rgba(0.70, 0.53, 1.0, 0.55) : Qt.rgba(1, 1, 1, 0.12)
    }

    contentItem: ColumnLayout {
        spacing: 0

        Item {
            Layout.fillWidth: true
            Layout.preferredHeight: 56

            SwitchDelegate {
                anchors.fill: parent
                spacing: 0
                bottomPadding: 0
                topPadding: 0
                rightPadding: 16
                leftPadding: 16
                clip: false
                id: indicatCbx
                text: rootElement.title
                font.bold: true
                checked: rootElement.isOpen
                onClicked: {
                    rootElement.isOpen = checked;
                    if (typeof(settings[rootElement.linkedBoolSetting])=="undefined") {
                        settings.setValue(rootElement.linkedBoolSetting, rootElement.convertValue(checked));
                    }
                    else {
                        settings[rootElement.linkedBoolSetting] = rootElement.convertValue(checked);
                    }
                }
            }

            TextMetrics {
                id: titleMetrics
                font: indicatCbx.font
                text: rootElement.title
            }

            // "?" right after the title: shows or hides the description of the tile
            Button {
                id: helpButton
                visible: rootElement.helpText !== ""
                x: indicatCbx.leftPadding + titleMetrics.width + 10
                anchors.verticalCenter: parent.verticalCenter
                width: 28
                height: 28
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
                    color: rootElement.helpOpen ? Qt.rgba(0.49, 0.30, 1.0, 0.30) : "transparent"
                    border.width: 1
                    border.color: Qt.rgba(0.70, 0.53, 1.0, 0.55)
                }

                onClicked: rootElement.helpOpen = !rootElement.helpOpen

                Accessible.role: Accessible.Button
                Accessible.name: qsTr("Help")
                Accessible.description: rootElement.helpOpen ? qsTr("Hide the description of this tile") : qsTr("Show the description of this tile")
            }
        }

        Label {
            visible: rootElement.helpText !== "" && rootElement.helpOpen
            text: rootElement.helpText
            wrapMode: Text.WordWrap
            textFormat: Text.PlainText
            color: "#9a9aa8"
            font.pixelSize: Qt.application.font.pixelSize - 2
            Layout.fillWidth: true
            Layout.leftMargin: 16
            Layout.rightMargin: 16
            Layout.bottomMargin: 12
        }

        // This will get filled with the content
        ColumnLayout {
            id: contentPlaceholder
            visible: rootElement.isOpen
            Layout.fillWidth: true
            Layout.leftMargin: 16
            Layout.rightMargin: 16
            Layout.bottomMargin: 12
        }
    }
}
