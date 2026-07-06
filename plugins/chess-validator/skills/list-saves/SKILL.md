---
name: list-saves
description: List available Chess Validator save slots. Use when the user invokes list-saves or asks what saved chess games, checkpoints, or positions are available.
---

# List Saves

Use the sibling chess script at `../chess-play/scripts/chess_play.py` as the source of truth. In Codex, resolve `<this-skill-dir>` from this skill's source path before running commands; do not pass the placeholder literally. In Claude Code, `${CLAUDE_SKILL_DIR}` is this skill directory. Use `python3` on Unix/macOS; if unavailable, use `python` or `py -3` with the same arguments.

Run:

```bash
python3 <this-skill-dir>/../chess-play/scripts/chess_play.py list-saves --json
```

Claude Code form:

```bash
python3 "${CLAUDE_SKILL_DIR}/../chess-play/scripts/chess_play.py" list-saves --json
```

Show save names, move counts, and saved timestamps when present. Keep the output compact.
