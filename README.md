# Export Deck Guide as Text

Systematically organized Anki collections often encode substantial information in their deck names and hierarchies. However, a deck path such as `2.HEL::2.GRC::4.CAT::2.PRO::1.PHS::2.Ar.` is difficult to interpret without knowing what the abbreviations stand for, why the decks are arranged as they are, and what each branch is meant to contain. The deck **Description** provides a natural place for such documentation: it belongs to the deck it describes, can be read and edited within Anki, and remains with the collection.

This add-on exports all non-empty descriptions as structured text, either to the clipboard or to a file. For each entry, it records the deck’s full path and indicates whether Anki treats the description as Markdown or HTML. The resulting export can serve as a guide to the collection’s organization, useful for inspection and—above all—as context for an LLM.

**[Export Deck Guide as Text](https://github.com/schmidhauser/anki-export-deck-guide-as-text)** complements **[Export Deck Tree as Text](https://github.com/schmidhauser/anki-export-deck-tree-as-text)**, **[Export Field and Tag Legend as Text](https://github.com/schmidhauser/anki-export-field-tag-legend-as-text)**, **[Export Note Types as Text](https://github.com/schmidhauser/anki-export-note-types-as-text)**, and **[Export Tags as Text](https://github.com/schmidhauser/anki-export-tags-as-text)**. Together, these five add-ons provide collection-level context. In the Browser, **[Selected Notes to Structured Text](https://github.com/schmidhauser/anki-selected-notes-to-structured-text)** makes the selected notes available for assessment in that context or as exemplars for note generation.

## Installation

Install **Export Deck Guide as Text** from [AnkiWeb](https://ankiweb.net/shared/info/1938515620) using add-on code `1938515620`.

## Usage

<img src="export-deck-guide-as-text-1.png" alt="Export menu with Deck Guide as Text commands" align="right" width="320">

Choose either of the following menu items:

* **Export → Copy Deck Guide as Text**
* **Export → Save Deck Guide as Text…**

Both commands export the same collection-wide deck guide: **Copy Deck Guide as Text** places it on the clipboard; **Save Deck Guide as Text…** writes it to a UTF-8 text file, by default named `anki-deck-guide-YYYY-MM-DD.txt`.

The export contains normal decks only: filtered decks are excluded, and decks with empty descriptions are omitted. Descriptions are exported in Anki’s deck order.

Deck descriptions can be edited in Anki’s **Description** window. With **Markdown** enabled, the description is stored as Markdown and rendered by Anki accordingly.

<img src="export-deck-guide-as-text-2.png" alt="Markdown deck description and its rendered Anki display" width="1000">

The add-on only reads deck metadata; it does not modify the collection.

## Configuration

The keyboard shortcuts can be changed in the add-on’s configuration dialog:

**Tools → Add-ons → 𝕾 Export Deck Guide as Text → Config**

The default configuration is:

```json
{
    "shortcut_copy": "",
    "shortcut_save": "Meta+Ctrl+Shift+G"
}
```

`shortcut_copy` is disabled by default.

On macOS, Qt interprets `Meta` as Control (`⌃`), `Ctrl` as Command (`⌘`), `Alt` as Option (`⌥`), and `Shift` as Shift (`⇧`). The default shortcut for **Save Deck Guide as Text…** is therefore `⌃⇧⌘G`.

No restart is required.

## Format

The export begins with the number of deck descriptions exported and a short explanation of the format. Each description is then represented by an `anki-deck` block containing the deck’s full path and an `anki-description` block containing the description itself. An example:

```yaml
# ANKI DECK GUIDE

Deck descriptions exported: 2

Each `<@anki-deck>` block contains the description stored for one normal
Anki deck with a non-empty description, with leading and trailing whitespace
removed. The `format` attribute records whether Anki uses Markdown or
HTML for that description.

<@anki-deck name="2.HEL"@>
<@anki-description format="markdown"@>
# 2.HEL – Hellenic

This branch contains all Greek material. It is organized by **evidence layer**
– prehistoric, Mycenaean, alphabetic polytonic, alphabetic monotonic…
</@anki-description@>
</@anki-deck@>

<@anki-deck name="2.HEL::0.PHG"@>
<@anki-description format="markdown"@>
# 0.PHG – PREHISTORIC GREEK

`0.PHG` contains **reconstructed** material used…
</@anki-description@>
</@anki-deck@>
```

The `name` attribute records the deck’s full path as stored by Anki. The `format` attribute is `markdown` when **Markdown** is enabled for that description and `html` otherwise.

Leading and trailing whitespace is removed from each description; internal whitespace, Markdown, HTML, links, Unicode characters, and other content are otherwise preserved.

The `<@…@>` delimiters make deck and description boundaries explicit without requiring the description contents themselves to be transformed. The format is intended to be straightforward for humans to inspect and for LLMs to parse.

## Compatibility

Tested with Anki 26.08 on macOS Tahoe 26. Windows and Linux have not yet been tested.

Suggestions and bug reports are welcome. Please [open an issue on GitHub](https://github.com/schmidhauser/anki-export-deck-guide-as-text/issues).

## License

Licensed under the [GNU AGPL v3 or later](LICENSE).
