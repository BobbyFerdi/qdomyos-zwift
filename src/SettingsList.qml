import QtQuick 2.7
import Qt.labs.folderlistmodel 2.15
import QtQuick.Layouts 1.3
import QtQuick.Controls 2.15
import QtQuick.Controls.Material 2.0
import QtQuick.Dialogs 1.0

ColumnLayout {
    signal loadSettings(url name)

    Connections {
        target: rootItem
        function onAndroidDocumentPicked(kind, localUrl) {
            if (kind === "settings") {
                loadSettings(localUrl)
            }
        }
    }

    Loader {
        id: fileDialogLoader
        active: false
        sourceComponent: Component {
            FileDialog {
                title: qsTr("Please choose a file")
                folder: shortcuts.home
                visible: true
                onAccepted: {
                    console.log("You chose: " + fileUrl)
                    loadSettings(fileUrl)
                    close()
                    // Destroy and recreate the dialog for next use
                    fileDialogLoader.active = false
                }
                onRejected: {
                    console.log("Canceled")
                    close()
                    // Destroy the dialog
                    fileDialogLoader.active = false
                }
            }
        }
    }

    StaticAccordionElement {
        title: qsTr("Settings folder")
        indicatRectColor: Material.color(Material.Grey)
        textColor: Material.color(Material.Grey)
        color: Material.backgroundColor
        accordionContent: ColumnLayout {
            ListView {
                id: list
                anchors.fill: parent
                FolderListModel {
                    id: folderModel
                    nameFilters: ["*.qzs"]
                    folder: "file://" + rootItem.getWritableAppDir() + 'settings'
                    showDotAndDotDot: false
                    showDirs: true
                    sortReversed: true
                }
                model: folderModel
                delegate: Component {
                    Rectangle {
                        property alias textColor: fileTextBox.color
                        width: parent.width
                        height: 54
                        color: "transparent"
                        z: 1
                        // Card behind the row: the row itself is see-through so the selection shows over it
                        Rectangle {
                            anchors.fill: parent
                            anchors.margins: 3
                            anchors.leftMargin: 8
                            anchors.rightMargin: 8
                            radius: 12
                            color: Qt.lighter(Material.backgroundColor, 1.3)
                            z: -1
                        }
                        Text {
                            id: fileTextBox
                            color: Material.color(Material.Grey)
                            font.pixelSize: Qt.application.font.pixelSize * 1.35
                            text: fileName.substring(0, fileName.length-4)
                            leftPadding: window.contentSideMargin
                        }
                        MouseArea {
                            anchors.fill: parent
                            z: 100
                            onClicked: {
                                console.log('onclicked ' + index+ " count "+list.count);
                                if (index == list.currentIndex) {
                                    let fileUrl = folderModel.get(list.currentIndex, 'fileUrl') || folderModel.get(list.currentIndex, 'fileURL');
                                    if (fileUrl) {
                                        loadSettings(fileUrl);
                                    }
                                }
                                else {
                                    if (list.currentItem)
                                        list.currentItem.textColor = Material.color(Material.Grey)
                                    list.currentIndex = index
                                }
                            }
                        }
                    }
                }
                highlight: Rectangle {
                    color: "#7C4DFF"
                    z:3
                    radius: 12
                    opacity: 0.45
                    focus: true
                    /*Text {
                        anchors.centerIn: parent
                        text: 'Selected ' + folderModel.get(list.currentIndex, "fileName")
                        color: "white"
                    }*/
                }
                focus: true
                onCurrentItemChanged: {
                    let fileUrl = folderModel.get(list.currentIndex, 'fileUrl') || folderModel.get(list.currentIndex, 'fileURL');
                    if (fileUrl) {
                        list.currentItem.textColor = Material.color(Material.Yellow)
                        console.log(fileUrl + ' selected');
                    }
                }
            }
        }
    }
    spacing: 10

    Button {
        id: searchButton
        height: 50
        width: parent.width
        text: qsTr("Other folders")
        Layout.alignment: Qt.AlignCenter | Qt.AlignVCenter
        onClicked: {
            console.log("folder is " + rootItem.getWritableAppDir() + 'settings')
            if (Qt.platform.os === "android") {
                rootItem.openAndroidDocumentPicker("settings")
            } else {
                fileDialogLoader.active = true
            }
        }
        anchors {
            bottom: parent.bottom
        }
    }
}
