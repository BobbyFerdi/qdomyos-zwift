import QtQuick 2.7
import QtQuick.Layouts 1.3

ColumnLayout {
    id: rootElement
    property bool isOpen: false
    property string title: ""
    property alias color: accordionHeader.color
    property alias textColor: accordionText.color
    property alias textFont: accordionText.font.family
    property alias textFontSize: accordionText.font.pixelSize
    property alias indicatRectColor: indicatRect.color
    default property alias accordionContent: contentLoader.sourceComponent

    // Signal emitted when content becomes visible
    signal contentBecameVisible()

    spacing: 0
    Layout.fillWidth: true

    Rectangle {
        id: accordionHeader
        color: "red"
        Layout.alignment: Qt.AlignTop
        Layout.fillWidth: true
        Layout.topMargin: 6
        Layout.leftMargin: 8
        Layout.rightMargin: 8
        height: 52
        radius: 12
        // Header presses fade a little so the whole card feels tappable
        opacity: headerMouse.pressed ? 0.8 : 1.0
        Behavior on opacity { NumberAnimation { duration: 80 } }

        Accessible.role: Accessible.Button         
        Accessible.name: title 
        Accessible.description: expanded ? "Expanded" : "Collapsed"
        Accessible.onPressAction: toggle()

        Rectangle {
            id: indicatRect
            x: 18; y: 22
            width: 8; height: 8
            radius: 4
            color: "white"
        }

        Text {
            id: accordionText
            x: 40
            anchors.verticalCenter: parent.verticalCenter
            font.bold: true
            font.pixelSize: 15
            color: "#FFFFFF"
            text: rootElement.title
        }

        Image {
            anchors.verticalCenter: parent.verticalCenter
            anchors.right: parent.right
            anchors.rightMargin: 16
            width: 26; height: 26
            opacity: 0.85
            id: indicatImg
            // Bound to isOpen: a section opened from code (a search result) shows the right arrow
            source: rootElement.isOpen ? "qrc:/icons/arrow-expand-vertical.png" : "qrc:/icons/arrow-collapse-vertical.png"
        }

        MouseArea {
            id: headerMouse
            anchors.fill: parent
            cursorShape: Qt.PointingHandCursor
            onClicked: rootElement.isOpen = !rootElement.isOpen
        }
    }

    // Loader with enhanced visibility handling
    Loader {
        id: contentLoader
        active: rootElement.isOpen
        visible: false // Start invisible
        Layout.fillWidth: true
        asynchronous: false

        onLoaded: {
            if (item) {
                item.Layout.fillWidth = true
                visible = true
                rootElement.contentBecameVisible()
            }
        }

        // Handle visibility changes
        onVisibleChanged: {
            if (visible && status === Loader.Ready) {
                rootElement.contentBecameVisible()
            }
        }
    }

    // Handle accordion closing
    onIsOpenChanged: {
        if (!isOpen) {
            contentLoader.visible = false
        }
    }
}
