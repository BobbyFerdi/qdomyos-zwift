import QtQuick 2.7
import QtQuick.Layouts 1.3
import QtQuick.Controls 2.15
import QtQuick.Controls.Material 2.0
import Qt.labs.settings 1.0
import QtQuick.Dialogs 1.0

SwitchDelegate {
    id: root

    // Preserve Material styling while making translated setting titles responsive.
    function configureTextItem(item) {
        if (!item)
            return false

        if (item.wrapMode !== undefined && item.maximumLineCount !== undefined) {
            item.wrapMode = Text.WrapAtWordBoundaryOrAnywhere
            item.maximumLineCount = 2
            if (item.elide !== undefined)
                item.elide = Text.ElideRight
            return true
        }

        if (item.children) {
            for (var i = 0; i < item.children.length; ++i) {
                if (configureTextItem(item.children[i]))
                    return true
            }
        }

        return false
    }

    function configureContentItem() {
        configureTextItem(contentItem)
    }

    // description of the setting: shows as a "?" right after the title
    property string helpText: ""

    TextMetrics {
        id: titleMetrics
        font: root.font
        text: root.text
    }

    SettingHelpButton {
        helpText: root.helpText
        anchors.verticalCenter: parent.verticalCenter
        x: Math.min(root.leftPadding + titleMetrics.width + 10,
                    root.width - root.indicator.width - root.rightPadding - width - 8)
    }

    Component.onCompleted: Qt.callLater(configureContentItem)
    onContentItemChanged: Qt.callLater(configureContentItem)
    onTextChanged: Qt.callLater(configureContentItem)

    MouseArea {
        anchors.fill: parent
        onClicked: {
            if (mouse.x > parent.width - parent.indicator.width) {
                root.checked = !root.checked
                root.clicked()
            }
        }
    }
}
