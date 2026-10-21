import QtQuick 2.12
import QtQuick.Controls 2.5
import QtQuick.Controls.Material 2.12
import QtGraphicalEffects 1.12
import Qt.labs.settings 1.0

Page {

    title: qsTr("QZ Fitness")
    id: page

    // VoiceOver accessibility - ignore Page itself, only children are accessible
    Accessible.ignored: true

    property alias start: start
    property alias stop: stop
    property alias lap: lap
    property alias row: row
    // Search for the equipment ("Next search in 12 s"), set by Home.qml while no device is connected
    property string searchStatus: ""

    // Design tokens shared with the tile grid (Home.qml keeps its own copy of the same values)
    readonly property color accentColor: "#7C4DFF"
    readonly property color dangerColor: "#EF5350"
    readonly property color okColor: "#4CD27A"
    readonly property color surfaceColor: Qt.lighter(settings.theme_background_color, 1.35)

    Settings {
	     id: settings
		  property real ui_zoom: 100.0
		  property bool theme_tile_icon_enabled: true
		  property string theme_background_color: "#303030"
		}

    Item {
        width: parent.width
        height: rootItem.topBarHeight
        id: topBar
        visible: !window.lockTiles

        Row {
            id: row
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            height: topBar.height - 20
            spacing: 10
            padding: 5

            // Connection chip: Bluetooth icon with a live status dot. A tap searches right away
            // instead of waiting for the next search (with a device connected it does nothing)
            Rectangle {
                id: connectionChip
                width: 64
                height: row.height - 10
                anchors.verticalCenter: parent.verticalCenter
                radius: height / 2
                color: page.surfaceColor
                border.width: 1
                border.color: rootItem.device ? page.okColor : Qt.rgba(1, 1, 1, 0.12)
                Accessible.ignored: true

                Behavior on border.color { ColorAnimation { duration: 250 } }

                Image {
                    id: treadmill_connection
                    anchors.centerIn: parent
                    width: Math.min(parent.width - 24, parent.height - 24)
                    height: width
                    fillMode: Image.PreserveAspectFit
                    source: "icons/icons/bluetooth-icon.png"
                    enabled: rootItem.device
                    smooth: true
                    opacity: enabled ? 1.0 : 0.45

                    // VoiceOver accessibility
                    Accessible.role: Accessible.Indicator
                    Accessible.name: qsTr("Bluetooth connection")
                    Accessible.description: rootItem.device ? qsTr("Device connected") : qsTr("Device not connected")
                    Accessible.focusable: true
                }

                // Signal strength, tucked into the chip's corner
                Image {
                    id: treadmill_signal
                    anchors.right: parent.right
                    anchors.rightMargin: 6
                    anchors.bottom: parent.bottom
                    anchors.bottomMargin: 4
                    width: 16
                    height: 16
                    fillMode: Image.PreserveAspectFit
                    source: rootItem.signal
                    smooth: true
                    Accessible.ignored: true
                }

                // Status dot
                Rectangle {
                    width: 10
                    height: 10
                    radius: 5
                    anchors.top: parent.top
                    anchors.topMargin: 6
                    anchors.right: parent.right
                    anchors.rightMargin: 6
                    color: rootItem.device ? page.okColor : page.dangerColor
                    Behavior on color { ColorAnimation { duration: 250 } }
                }

                MouseArea {
                    anchors.fill: parent
                    onClicked: rootItem.bluetoothSearchNow()
                }
            }

            Button {
                icon.source: rootItem.startIcon
                icon.height: 26
                icon.width: 26
                icon.color: "white"
                text: rootItem.startText
                enabled: true
                id: start
                width: 128
                height: row.height - 10
                anchors.verticalCenter: parent.verticalCenter
                font.bold: true
                font.pixelSize: 15
                palette.buttonText: "white"

                background: Rectangle {
                    radius: height / 2
                    color: rootItem.startColor === "red" ? page.dangerColor : page.accentColor
                    opacity: start.down ? 0.75 : 1.0
                    scale: start.down ? 0.97 : 1.0
                    Behavior on opacity { NumberAnimation { duration: 80 } }
                    Behavior on scale { NumberAnimation { duration: 80 } }
                }

                // VoiceOver accessibility
                Accessible.role: Accessible.Button
                Accessible.name: rootItem.startText
                Accessible.description: qsTr("Start workout")
                Accessible.focusable: true
            }

            Button {
                icon.source: rootItem.stopIcon
                icon.height: 26
                icon.width: 26
                icon.color: "white"
                text: rootItem.stopText
                enabled: true
                id: stop
                width: 128
                height: row.height - 10
                anchors.verticalCenter: parent.verticalCenter
                font.bold: true
                font.pixelSize: 15
                palette.buttonText: "white"

                background: Rectangle {
                    radius: height / 2
                    // Tonal until it matters: red when the app flags the stop as the primary action
                    color: rootItem.stopColor === "red" ? page.dangerColor : page.surfaceColor
                    border.width: rootItem.stopColor === "red" ? 0 : 1
                    border.color: Qt.rgba(1, 1, 1, 0.12)
                    opacity: stop.down ? 0.75 : 1.0
                    scale: stop.down ? 0.97 : 1.0
                    Behavior on opacity { NumberAnimation { duration: 80 } }
                    Behavior on scale { NumberAnimation { duration: 80 } }
                }

                // VoiceOver accessibility
                Accessible.role: Accessible.Button
                Accessible.name: rootItem.stopText
                Accessible.description: qsTr("Stop workout")
                Accessible.focusable: true
            }

            RoundButton {
                id: lap
                width: row.height - 10
                height: row.height - 10
                anchors.verticalCenter: parent.verticalCenter
                icon.source: "icons/icons/lap.png"
                icon.width: 28
                icon.height: 28
                icon.color: "white"
                enabled: rootItem.lap
                smooth: true
                opacity: enabled ? 1.0 : 0.4

                background: Rectangle {
                    radius: width / 2
                    color: page.surfaceColor
                    border.width: 1
                    border.color: Qt.rgba(1, 1, 1, 0.12)
                    scale: lap.down ? 0.94 : 1.0
                    Behavior on scale { NumberAnimation { duration: 80 } }
                }

                // VoiceOver accessibility
                Accessible.role: Accessible.Button
                Accessible.name: qsTr("Lap")
                Accessible.description: qsTr("Record a new lap")
                Accessible.focusable: true
            }
        }

        Row {
            id: row1
            width: parent.width
            anchors.bottom: row.bottom
            anchors.bottomMargin: -10

            Label {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
                // the search status may have two lines ("<device> found" and the countdown): the line
                // grows upwards, so they are set closer to keep the first one off the buttons
                horizontalAlignment: Text.AlignHCenter
                lineHeight: text.indexOf("\n") >= 0 ? 0.8 : 1
                font.pixelSize: 12
                opacity: 0.9
                text: page.searchStatus !== "" ? page.searchStatus : rootItem.info
            }
        }

        Label {
            id: lblHelp
            width: parent.width
            leftPadding: window.contentSideMargin
            rightPadding: window.contentSideMargin
            anchors.top: row1.bottom
            anchors.topMargin: 30
            text: qsTr("This app should automatically connect to your bike/treadmill/rower. <b>If it doesn't, please check</b>:<br>1) your Echelon/Domyos App MUST be closed while qdomyos-zwift is running;<br>2) both Bluetooth and Bluetooth permissions MUST be enabled<br>3) your bike/treadmill/rower should be turned on BEFORE starting this app<br>4) try to restart your device<br><br>If your bike/treadmill disconnects every 30 seconds try to disable the 'virtual device' setting on the left bar.<br><br>In case of issues, please feel free to contact me at roberto.viola83@gmail.com.<br><br><b>Have a nice ride!</b><br/ ><i>QZ specifically disclaims liability for<br>incidental or consequential damages and assumes<br>no responsibility or liability for any loss<br>or damage suffered by any person as a result of<br>the use or misuse of the app.</i><br><br>Roberto Viola")
            wrapMode: Label.WordWrap
            visible: rootItem.labelHelp
        }
    }
}

/*##^##
Designer {
    D{i:0;autoSize:true;formeditorZoom:0.6600000262260437;height:480;width:640}
}
##^##*/

