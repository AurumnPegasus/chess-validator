# Changelog

## 0.2.1

- Reorganize the chess CLI into dependency, persistence, board, command, output, and CLI sections.
- Move automatic `python-chess` bootstrap out of the plugin directory and into a user-writable cache.
- Return structured JSON for invalid save names instead of Python tracebacks.
- Support natural save names with spaces and punctuation.
- Expand validation coverage for save/load edge cases and dependency-cache behavior.

## 0.2.0

- Package the project as Codex and Claude Code marketplace plugins.
- Add command-style skill aliases: `new-game`, `save-game`, `load-game`, `list-saves`, `show-board`, and `legal-moves`.
- Add JSON save/load support to the bundled chess referee script.
- Add public validation tooling and CI.

## 0.1.0

- Initial Chess Validator skill and local chess referee script.
