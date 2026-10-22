#!/usr/bin/env python3
"""Calm the look of the settings pages (TrainDeck).

The settings QML files repeat the same two patterns hundreds of times:

* a help Label in bright yellow-green, bold and italic, under every setting
* a heavy grey "OK" Button next to every number / text field

This script restyles both in place:

* the help text becomes muted grey, regular weight; and every help Label that only uses the usual properties
  becomes a SettingHelp (src/SettingHelp.qml): a small "?" button that shows the description when tapped
* the OK buttons become flat accent-coloured buttons

It only changes style and the help Label itself, never a setting, a binding or a layout, and running it twice
changes nothing the second time. Help Labels with anything unusual in them (nested items, handlers, other
properties) are left as muted Labels.

Run it from the repository root, and again after merging updates from the original repository, because
new settings arrive with the old styling:

    python tools/restyle_settings.py            # restyle the files
    python tools/restyle_settings.py --check    # only report what would change (exit 1 if anything would)
"""

import sys
from pathlib import Path

FILES = [
    "src/settings.qml",
    "src/settings-tiles.qml",
    "src/settings-tts.qml",
    "src/settings-shortcuts.qml",
    "src/settings-treadmill-inclination-override.qml",
]

OLD_HELP_COLOR = "color: Material.color(Material.Lime)"
NEW_HELP_COLOR = 'color: "#9a9aa8"'
OK_BUTTON_TEXT = 'text: qsTr("OK")'
OK_BUTTON_COLOR = 'Material.foreground: "#B388FF"'

# the properties a help Label may set for it to become a SettingHelp, which supports exactly these
HELP_PROPERTIES = {
    "text", "color", "font.bold", "font.italic", "font.pixelSize", "wrapMode", "textFormat",
    "verticalAlignment", "visible", "Layout.fillWidth", "Layout.alignment",
    "width",  # overridden by the layout anyway once the item fills the row
}


def indent_of(line):
    return len(line) - len(line.lstrip())


def block_end(lines, start):
    """Index of the closing brace of the block opened on lines[start] (same indentation), or -1."""
    indent = indent_of(lines[start])
    for j in range(start + 1, len(lines)):
        if lines[j].strip() == "}" and indent_of(lines[j]) == indent:
            return j
    return -1


def is_plain_help(lines, start, end):
    """True when the Label at lines[start] uses only the properties SettingHelp supports and has nothing nested."""
    indent = indent_of(lines[start])
    for k in range(start + 1, end):
        stripped = lines[k].strip()
        if stripped.startswith("//"):
            continue  # a commented-out line
        if "{" in stripped or "}" in stripped:
            return False
        if indent_of(lines[k]) == indent + 4 and stripped:
            if stripped.split(":")[0].strip() not in HELP_PROPERTIES:
                return False
    return True


def restyle(text):
    """Return (new_text, help_labels_restyled, help_buttons_added, ok_buttons_restyled)."""
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.replace("\r\n", "\n").split("\n")
    has_material = any(line.strip().startswith("import QtQuick.Controls.Material") for line in lines)
    help_changed = 0
    help_buttons = 0
    ok_changed = 0

    # help labels: muted colour, no bold, no italic
    i = 0
    while i < len(lines):
        if lines[i].strip() == "Label {":
            end = block_end(lines, i)
            if end > i:
                block = lines[i + 1:end]
                if any(line.strip() == OLD_HELP_COLOR for line in block):
                    for k in range(i + 1, end):
                        stripped = lines[k].strip()
                        pad = lines[k][:indent_of(lines[k])]
                        if stripped == OLD_HELP_COLOR:
                            lines[k] = pad + NEW_HELP_COLOR
                        elif stripped == "font.bold: true":
                            lines[k] = pad + "font.bold: false"
                        elif stripped == "font.italic: true":
                            lines[k] = pad + "font.italic: false"
                    help_changed += 1
        i += 1

    # muted help labels that only use the usual properties become a tap-to-reveal SettingHelp
    i = 0
    while i < len(lines):
        if lines[i].strip() == "Label {":
            end = block_end(lines, i)
            if end > i and any(line.strip() == NEW_HELP_COLOR for line in lines[i + 1:end]) \
                    and is_plain_help(lines, i, end):
                lines[i] = lines[i].replace("Label {", "SettingHelp {", 1)
                help_buttons += 1
        i += 1

    # OK buttons: flat, accent coloured text (inserted right after the text line, so the order stays readable)
    i = 0
    while i < len(lines):
        if lines[i].strip() == "Button {":
            end = block_end(lines, i)
            if end > i:
                block = [line.strip() for line in lines[i + 1:end]]
                if OK_BUTTON_TEXT in block and "flat: true" not in block:
                    at = next(k for k in range(i + 1, end) if lines[k].strip() == OK_BUTTON_TEXT)
                    pad = lines[at][:indent_of(lines[at])]
                    extra = [pad + "flat: true"]
                    if has_material:
                        extra.append(pad + OK_BUTTON_COLOR)
                    lines[at + 1:at + 1] = extra
                    ok_changed += 1
        i += 1

    return newline.join(lines), help_changed, help_buttons, ok_changed


def main():
    check_only = "--check" in sys.argv[1:]
    root = Path(__file__).resolve().parent.parent
    total_help = total_buttons = total_ok = 0
    for name in FILES:
        path = root / name
        if not path.exists():
            print("skipped (not found): %s" % name)
            continue
        original = path.read_text(encoding="utf-8", newline="")
        updated, help_changed, help_buttons, ok_changed = restyle(original)
        print("%-50s muted: %-4d help buttons: %-4d OK buttons: %-4d" % (name, help_changed, help_buttons, ok_changed))
        total_help += help_changed
        total_buttons += help_buttons
        total_ok += ok_changed
        if not check_only and updated != original:
            path.write_text(updated, encoding="utf-8", newline="")
    print("total: %d help labels muted, %d turned into help buttons, %d OK buttons restyled %s"
          % (total_help, total_buttons, total_ok, "(would change)" if check_only else ""))
    if check_only and (total_help or total_buttons or total_ok):
        sys.exit(1)


if __name__ == "__main__":
    main()
