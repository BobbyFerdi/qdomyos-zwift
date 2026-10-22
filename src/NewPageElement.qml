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
    property string accordionContent: ""
    spacing: 0

    Layout.fillWidth: true;

    Rectangle {
        id: accordionHeader
        color: "red"
        Layout.alignment: Qt.AlignTop
        Layout.fillWidth: true;
        Layout.topMargin: 6
        Layout.leftMargin: 8
        Layout.rightMargin: 8
        height: 52
        radius: 12
        border.width: 1
        border.color: Qt.rgba(1, 1, 1, 0.14)

        Accessible.role: Accessible.Button 
        Accessible.name: title 
        Accessible.description: expanded ? "Expanded" : "Collapsed"
        Accessible.onPressAction: toggle()

        Rectangle{
           id:indicatRect
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
        Text {
            anchors.verticalCenter: parent.verticalCenter
            anchors.right:  parent.right
            anchors.rightMargin: 20
            width: 30; height: 30
            verticalAlignment: Text.AlignVCenter
            id: indicatImg
            text: ">"
            font.pixelSize: 24
            color: "white"
        }
        MouseArea {
            anchors.fill: parent
            cursorShape: Qt.PointingHandCursor
            onClicked: {
                stackView.push(accordionContent)
            }
        }
    }
}
