---
name: load-game
description: Load a named Chess Validator save slot into the current game. Use when the user invokes load-game, asks to restore a chess game, continue from a saved position, or return to a checkpoint.
---

# Load Game

Use the sibling chess script at `../chess-play/scripts/chess_play.py` as the source of truth. In Codex, resolve `<this-skill-dir>` from this skill's source path before running commands; do not pass the placeholder literally. In Claude Code, `${CLAUDE_SKILL_DIR}` is this skill directory.

Use any argument supplied after the command as the save name. In Claude Code, command arguments are `$ARGUMENTS`; use `$ARGUMENTS` as the save name when it is non-empty. If no name is supplied, use `default`.

Run:

```bash
python3 <this-skill-dir>/../chess-play/scripts/chess_play.py load-game <name> --json
```

Claude Code form:

```bash
python3 "${CLAUDE_SKILL_DIR}/../chess-play/scripts/chess_play.py" load-game <name> --json
```

If `loaded` is false, report the reason and suggest `list-saves`. If loaded, render the board, last move, and side to move.
