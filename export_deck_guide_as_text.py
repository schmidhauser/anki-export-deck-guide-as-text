# Copyright (C) 2026 Andreas U. Schmidhauser
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import date
from html import escape
from pathlib import Path

from anki.decks import DeckId
from aqt import mw
from aqt.qt import (
    QAction,
    QApplication,
    QFileDialog,
    QMenu,
    qconnect,
)
from aqt.utils import showWarning, tooltip


EXPORT_MENU_OBJECT_NAME = "schmidhauser_export_menu"
EXPORT_GROUP_PROPERTY = "schmidhauser_export_group"


def get_export_menu() -> QMenu:
    menu_bar = mw.menuBar()
    assert menu_bar is not None

    existing_menu = menu_bar.findChild(QMenu, EXPORT_MENU_OBJECT_NAME)
    if existing_menu is not None:
        return existing_menu

    export_menu = QMenu("Export", menu_bar)
    export_menu.setObjectName(EXPORT_MENU_OBJECT_NAME)
    menu_bar.insertMenu(mw.form.menuHelp.menuAction(), export_menu)

    return export_menu


def add_export_action_group(
    group_name: str,
    copy_action: QAction,
    save_action: QAction,
) -> None:
    export_menu = get_export_menu()

    copy_action.setProperty(EXPORT_GROUP_PROPERTY, group_name)
    save_action.setProperty(EXPORT_GROUP_PROPERTY, group_name)

    sort_key = group_name.casefold()

    before_action = next(
        (
            action
            for action in export_menu.actions()
            if isinstance(
                existing_group := action.property(EXPORT_GROUP_PROPERTY),
                str,
            )
            and existing_group.casefold() > sort_key
        ),
        None,
    )

    if before_action is None:
        if export_menu.actions():
            export_menu.addSeparator()

        export_menu.addAction(copy_action)
        export_menu.addAction(save_action)
    else:
        export_menu.insertAction(before_action, copy_action)
        export_menu.insertAction(before_action, save_action)
        export_menu.insertSeparator(before_action)


def get_deck_descriptions() -> list[tuple[str, str, str]] | None:
    if mw.col is None:
        showWarning("No collection is open.", parent=mw)
        return None

    deck_names_and_ids = mw.col.decks.all_names_and_ids(
        skip_empty_default=False,
        include_filtered=False,
    )

    descriptions: list[tuple[str, str, str]] = []

    for deck_name_and_id in deck_names_and_ids:
        deck = mw.col.decks.get(
            DeckId(deck_name_and_id.id),
            default=False,
        )

        if deck is None:
            continue

        description = deck.get("desc", "")

        if not isinstance(description, str) or not description.strip():
            continue

        description_format = (
            "markdown" if bool(deck.get("md", False)) else "html"
        )

        descriptions.append(
            (
                deck_name_and_id.name,
                description.strip(),
                description_format,
            )
        )

    return descriptions


def format_deck_guide(
    descriptions: list[tuple[str, str, str]],
) -> str:
    blocks: list[str] = []

    for deck_name, description, description_format in descriptions:
        escaped_name = escape(deck_name, quote=True)

        lines = [
            f'<@anki-deck name="{escaped_name}"@>',
            f'<@anki-description format="{description_format}"@>',
            description,
            "</@anki-description@>",
            "</@anki-deck@>",
        ]
        blocks.append("\n".join(lines))

    preamble = [
        "# ANKI DECK GUIDE",
        "",
        f"Deck descriptions exported: {len(descriptions)}",
        "",
        (
            "Each `<@anki-deck>` block contains the description stored "
            "for one normal Anki deck with a non-empty description, with "
            "leading and trailing whitespace removed. The `format` attribute "
            "records whether Anki uses Markdown or legacy HTML handling for "
            "that description."
        ),
        "",
        "",
    ]

    return "\n".join(preamble) + "\n\n".join(blocks) + "\n"


def prepare_deck_guide() -> tuple[str, int] | None:
    descriptions = get_deck_descriptions()

    if descriptions is None:
        return None

    if not descriptions:
        showWarning(
            "No normal decks have non-empty descriptions.",
            parent=mw,
        )
        return None

    return format_deck_guide(descriptions), len(descriptions)


def result_message(verb: str, total: int) -> str:
    description_word = "description" if total == 1 else "descriptions"
    return f"{verb} Deck Guide ({total} deck {description_word})."


def on_copy() -> None:
    prepared = prepare_deck_guide()

    if prepared is None:
        return

    text, total = prepared

    clipboard = QApplication.clipboard()
    if clipboard is None:
        showWarning("Could not access the clipboard.", parent=mw)
        return

    clipboard.setText(text)

    tooltip(
        result_message("Copied", total),
        parent=mw,
    )


def on_save() -> None:
    prepared = prepare_deck_guide()

    if prepared is None:
        return

    text, total = prepared

    default_filename = (
        f"anki-deck-guide-{date.today().isoformat()}.txt"
    )
    default_path = Path.home() / default_filename

    filename, _selected_filter = QFileDialog.getSaveFileName(
        mw,
        "Save Deck Guide as Text",
        str(default_path),
        "Text Files (*.txt)",
    )

    if not filename:
        return

    path = Path(filename)

    if not path.suffix:
        path = path.with_suffix(".txt")

    try:
        path.write_bytes(text.encode("utf-8"))
    except OSError as error:
        showWarning(
            f"Could not save the file:\n{error}",
            parent=mw,
        )
        return

    tooltip(
        result_message("Saved", total),
        parent=mw,
    )


def apply_shortcuts(config: dict) -> None:
    shortcut_copy = config.get("shortcut_copy", "")
    shortcut_save = config.get("shortcut_save", "")

    copy_action.setShortcut(
        shortcut_copy if isinstance(shortcut_copy, str) else ""
    )
    save_action.setShortcut(
        shortcut_save if isinstance(shortcut_save, str) else ""
    )


copy_action = QAction("Copy Deck Guide as Text", mw)
save_action = QAction("Save Deck Guide as Text…", mw)

qconnect(copy_action.triggered, on_copy)
qconnect(save_action.triggered, on_save)

config = mw.addonManager.getConfig(__name__) or {}
apply_shortcuts(config)

mw.addonManager.setConfigUpdatedAction(__name__, apply_shortcuts)

# "Deck Tree Guide" is the hidden sort key that keeps Deck Guide
# immediately after Deck Tree in the shared Export menu.
add_export_action_group(
    "Deck Tree Guide",
    copy_action,
    save_action,
)
