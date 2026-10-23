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


# pages whose items are cards (AccordionCheckElement): a help button follows a card, so it is not pulled up
CARD_PAGES = {"src/settings-tiles.qml"}


def restyle(text, card_page=False):
    """Return (new_text, counts) where counts says how many of each kind of item were changed."""
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.replace("\r\n", "\n").split("\n")
    has_material = any(line.strip().startswith("import QtQuick.Controls.Material") for line in lines)
    counts = {"help muted": 0, "help buttons": 0, "buttons": 0, "titles": 0, "hints": 0, "card help spacing": 0, "card help folded": 0, "inline help": 0, "label wrap": 0, "stacked help": 0}

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

    # on a card page the help button sits below a card: normal spacing and the card's own right inset, not the
    # negative top margin that tucks it under a settings row
    if card_page:
        i = 0
        while i < len(lines):
            if lines[i].strip() == "SettingHelp {":
                end = block_end(lines, i)
                if end > i:
                    block = [line.strip() for line in lines[i + 1:end]]
                    if not any(s.startswith("Layout.rightMargin") for s in block):
                        at = next((k for k in range(i + 1, end) if lines[k].strip() == "Layout.fillWidth: true"), None)
                        if at is not None:
                            pad = lines[at][:indent_of(lines[at])]
                            lines[at + 1:at + 1] = [pad + "Layout.topMargin: 4", pad + "Layout.rightMargin: 8"]
                            counts["card help spacing"] += 1
            i += 1

    # on a card page the help of a card moves into the card: a "?" right after the card's title (helpText).
    # Only a SettingHelp that directly follows the card at the same indentation and has a one-line text moves.
    if card_page:
        i = 0
        while i < len(lines):
            if lines[i].strip() == "AccordionCheckElement {":
                end = block_end(lines, i)
                nxt = end + 1
                while end > i and nxt < len(lines) and lines[nxt].strip() == "":
                    nxt += 1
                if end > i and nxt < len(lines) and lines[nxt].strip() == "SettingHelp {" \
                        and indent_of(lines[nxt]) == indent_of(lines[i]):
                    help_end = block_end(lines, nxt)
                    card_has_help = any(line.strip().startswith("helpText:") for line in lines[i + 1:end])
                    text_line = next((lines[k].strip() for k in range(nxt + 1, help_end)
                                      if lines[k].strip().startswith("text:")), None)
                    title_at = next((k for k in range(i + 1, end)
                                     if indent_of(lines[k]) == indent_of(lines[i]) + 4
                                     and lines[k].strip().startswith("title:")), None)
                    if help_end > nxt and not card_has_help and text_line is not None and title_at is not None:
                        pad = lines[title_at][:indent_of(lines[title_at])]
                        lines[title_at + 1:title_at + 1] = [pad + "helpText:" + text_line[len("text:"):]]
                        shift = 1
                        stop = help_end + shift + 1
                        if stop < len(lines) and lines[stop].strip() == "":
                            stop += 1  # the blank line that separated the help from what follows
                        del lines[nxt + shift:stop]
                        counts["card help folded"] += 1
            i += 1

    # help of an ordinary setting moves next to its title: into the switch (helpText) or, for a row that starts
    # with a Label, a SettingHelpButton right after that Label. Only a SettingHelp that directly follows the
    # item at the same indentation and has a one-line text moves; any other stays below the row.
    if not card_page:
        i = 0
        while i < len(lines):
            opener = lines[i].strip()
            if opener in ("IndicatorOnlySwitch {", "RowLayout {"):
                end = block_end(lines, i)
                nxt = end + 1
                while end > i and nxt < len(lines) and lines[nxt].strip() == "":
                    nxt += 1
                if end > i and nxt < len(lines) and lines[nxt].strip() == "SettingHelp {" \
                        and indent_of(lines[nxt]) == indent_of(lines[i]):
                    help_end = block_end(lines, nxt)
                    help_lines = [line.strip() for line in lines[nxt + 1:help_end]]
                    text_line = next((s for s in help_lines if s.startswith("text:")), None)
                    # a row that already has its "?" takes no second help: that one belongs to another setting
                    has_help = any(line.strip() == "SettingHelpButton {" or line.strip().startswith("helpText:")
                                   for line in lines[i + 1:end])
                    movable = help_end > nxt and text_line is not None and text_line.endswith(")") \
                        and not has_help and not any(s.startswith("visible:") for s in help_lines)
                    pad_in = " " * (indent_of(lines[i]) + 4)
                    if movable and opener == "IndicatorOnlySwitch {":
                        at = next((k for k in range(i + 1, end) if indent_of(lines[k]) == len(pad_in)
                                   and lines[k].strip().startswith("text:")), None)
                        if at is not None and not any(line.strip().startswith("helpText:") for line in lines[i + 1:end]):
                            lines[at + 1:at + 1] = [pad_in + "helpText:" + text_line[len("text:"):]]
                            insert = "switch"
                        else:
                            insert = None
                    elif movable:
                        label_at = next((k for k in range(i + 1, end) if lines[k].strip() == "Label {"
                                         and indent_of(lines[k]) == len(pad_in)), None)
                        if label_at is not None and label_at == next(
                                k for k in range(i + 1, end) if lines[k].strip().endswith("{")):
                            label_end = block_end(lines, label_at)
                            lines[label_end + 1:label_end + 1] = [
                                pad_in + "SettingHelpButton {",
                                pad_in + "    helpText:" + text_line[len("text:"):],
                                pad_in + "    Layout.alignment: Qt.AlignVCenter",
                                pad_in + "}",
                            ]
                            insert = "row"
                        else:
                            insert = None
                    else:
                        insert = None
                    if insert:
                        shift = 1 if insert == "switch" else 4
                        stop = help_end + shift + 1
                        if stop < len(lines) and lines[stop].strip() == "":
                            stop += 1
                        del lines[nxt + shift:stop]
                        counts["inline help"] += 1
            i += 1

    # two "?" buttons one under the other would overlap (each is pulled up under the row above): space the lower one
    if not card_page:
        for i in range(len(lines) - 1, -1, -1):  # from the end, so an insert never moves a line still to visit
            if lines[i].strip() != "SettingHelp {":
                continue
            prev = i - 1
            while prev >= 0 and lines[prev].strip() == "":
                prev -= 1
            if prev < 0 or lines[prev].strip() != "}" or indent_of(lines[prev]) != indent_of(lines[i]):
                continue
            opener_at = next((k for k in range(prev - 1, -1, -1) if indent_of(lines[k]) == indent_of(lines[prev])
                              and lines[k].strip() != ""), None)
            if opener_at is None or lines[opener_at].strip() != "SettingHelp {":
                continue
            end = block_end(lines, i)
            if end > i and not any(line.strip().startswith("Layout.topMargin") for line in lines[i + 1:end]):
                at = next((k for k in range(i + 1, end) if lines[k].strip() == "Layout.fillWidth: true"), None)
                if at is not None:
                    lines.insert(at + 1, lines[at][:indent_of(lines[at])] + "Layout.topMargin: 8")
                    counts["stacked help"] += 1

    # a long label next to a "?" wraps instead of running under it
    if not card_page:
        for i in range(len(lines) - 1, -1, -1):  # from the end, so an insert never moves a line still to visit
            if lines[i].strip() != "SettingHelpButton {":
                continue
            close = i - 1
            if lines[close].strip() != "}" or indent_of(lines[close]) != indent_of(lines[i]):
                continue
            open_at = next((k for k in range(close - 1, -1, -1)
                            if indent_of(lines[k]) == indent_of(lines[close]) and lines[k].strip() != ""), None)
            if open_at is None or lines[open_at].strip() != "Label {":
                continue
            if not any(line.strip().startswith("wrapMode:") for line in lines[open_at + 1:close]):
                lines.insert(close, " " * (indent_of(lines[close]) + 4) + "wrapMode: Text.WordWrap")
                counts["label wrap"] += 1

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
        updated, counts = restyle(original, card_page=name in CARD_PAGES)
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
