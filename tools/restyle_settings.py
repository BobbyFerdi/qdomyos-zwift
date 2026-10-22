#!/usr/bin/env python3
"""Calm the look of the settings pages (TrainDeck).

The settings QML files repeat the same few patterns hundreds of times, in the original loud styling:

* a help Label in bright yellow-green, bold and italic, under every setting
* a heavy grey Button ("OK", "Refresh Devices List", ...) next to or under the fields
* sub-section titles in bright yellow or blue
* warning and hint Labels in bold italic red, orange or blue

This script restyles all of them in place:

* the help text becomes muted grey, regular weight; and every help Label that only uses the usual properties
  becomes a SettingHelp (src/SettingHelp.qml): a small "?" button that shows the description when tapped
* buttons become flat, accent-coloured text buttons
* sub-section titles become the soft brand violet
* warning and hint Labels keep their meaning (red stays red) but lose the bold italic and get softer shades

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
BUTTON_COLOR = 'Material.foreground: "#B388FF"'

# the properties a help Label may set for it to become a SettingHelp, which supports exactly these
HELP_PROPERTIES = {
    "text", "color", "font.bold", "font.italic", "font.pixelSize", "wrapMode", "textFormat",
    "verticalAlignment", "visible", "Layout.fillWidth", "Layout.alignment",
    "width",  # overridden by the layout anyway once the item fills the row
}

# sub-section titles: the loud colours become the soft brand violet (red stays: those sections are risky ones)
SUBSECTION_TITLE_COLORS = {
    "textColor: Material.color(Material.Yellow)": 'textColor: "#B388FF"',
    "textColor: Material.color(Material.Blue)": 'textColor: "#B388FF"',
}

# warning / hint Labels: same meaning, softer shade, no bold italic
HINT_COLORS = {
    "color: Material.color(Material.Red)": 'color: "#FF8A80"',
    "color: Material.color(Material.Orange)": 'color: "#FFB74D"',
    'color: "steelblue"': 'color: "#90CAF9"',
    "color: Material.color(Material.Grey)": NEW_HELP_COLOR,
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
    """Return (new_text, counts) where counts says how many of each kind of item were changed."""
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.replace("\r\n", "\n").split("\n")
    has_material = any(line.strip().startswith("import QtQuick.Controls.Material") for line in lines)
    counts = {"help muted": 0, "help buttons": 0, "buttons": 0, "titles": 0, "hints": 0}

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
                    counts["help muted"] += 1
        i += 1

    # warning / hint labels that are still bold or italic: softer shade, regular weight
    i = 0
    while i < len(lines):
        if lines[i].strip() == "Label {":
            end = block_end(lines, i)
            if end > i:
                stripped_block = [line.strip() for line in lines[i + 1:end]]
                if "font.italic: true" in stripped_block and any(s in HINT_COLORS for s in stripped_block):
                    for k in range(i + 1, end):
                        stripped = lines[k].strip()
                        pad = lines[k][:indent_of(lines[k])]
                        if stripped in HINT_COLORS:
                            lines[k] = pad + HINT_COLORS[stripped]
                        elif stripped == "font.bold: true":
                            lines[k] = pad + "font.bold: false"
                        elif stripped == "font.italic: true":
                            lines[k] = pad + "font.italic: false"
                    counts["hints"] += 1
        i += 1

    # muted help labels that only use the usual properties become a tap-to-reveal SettingHelp
    i = 0
    while i < len(lines):
        if lines[i].strip() == "Label {":
            end = block_end(lines, i)
            if end > i and any(line.strip() == NEW_HELP_COLOR for line in lines[i + 1:end]) \
                    and is_plain_help(lines, i, end):
                lines[i] = lines[i].replace("Label {", "SettingHelp {", 1)
                counts["help buttons"] += 1
        i += 1

    # sub-section titles: soft violet instead of bright yellow or blue
    for k in range(len(lines)):
        stripped = lines[k].strip()
        if stripped in SUBSECTION_TITLE_COLORS:
            lines[k] = lines[k][:indent_of(lines[k])] + SUBSECTION_TITLE_COLORS[stripped]
            counts["titles"] += 1

    # buttons with a text: flat, accent coloured text (inserted right after the text line, so the order stays
    # readable). Buttons that already are flat, are the primary action (highlighted) or draw their own
    # background are left alone.
    i = 0
    while i < len(lines):
        if lines[i].strip() == "Button {":
            end = block_end(lines, i)
            if end > i:
                block = [line.strip() for line in lines[i + 1:end]]
                has_text = any(s.startswith("text:") for s in block)
                skip = "flat: true" in block or "highlighted: true" in block \
                    or any(s.startswith("background:") for s in block)
                if has_text and not skip:
                    at = next(k for k in range(i + 1, end) if lines[k].strip().startswith("text:"))
                    pad = lines[at][:indent_of(lines[at])]
                    extra = [pad + "flat: true"]
                    if has_material:
                        extra.append(pad + BUTTON_COLOR)
                    lines[at + 1:at + 1] = extra
                    counts["buttons"] += 1
        i += 1

    return newline.join(lines), counts


def main():
    check_only = "--check" in sys.argv[1:]
    root = Path(__file__).resolve().parent.parent
    totals = {}
    for name in FILES:
        path = root / name
        if not path.exists():
            print("skipped (not found): %s" % name)
            continue
        original = path.read_text(encoding="utf-8", newline="")
        updated, counts = restyle(original)
        print("%-50s %s" % (name, "  ".join("%s: %d" % (k, v) for k, v in counts.items())))
        for key, value in counts.items():
            totals[key] = totals.get(key, 0) + value
        if not check_only and updated != original:
            path.write_text(updated, encoding="utf-8", newline="")
    print("total: " + ", ".join("%d %s" % (v, k) for k, v in totals.items()) + (" (would change)" if check_only else ""))
    if check_only and any(totals.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
