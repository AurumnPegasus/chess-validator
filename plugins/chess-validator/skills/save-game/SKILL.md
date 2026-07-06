---
name: save-game
description: Save the current Chess Validator game position to a named save slot. Use when the user invokes save-game, asks to save the current chess game, checkpoint a position, or preserve a game before trying a line.
---

# Save Game

Use the sibling chess script at `../chess-play/scripts/chess_play.py` as the source of truth. In Codex, resolve `<this-skill-dir>` from this skill's source path before running commands; do not pass the placeholder literally. In Claude Code, `${CLAUDE_SKILL_DIR}` is this skill directory.

Use any argument supplied after the command as the save name. In Claude Code, command arguments are `$ARGUMENTS`; use `$ARGUMENTS` as the save name when it is non-empty. If no name is supplied, use `default`.

Run:

```bash
python3 <this-skill-dir>/../chess-play/scripts/chess_play.py save-game <name> --json
```

Claude Code form:

```bash
python3 "${CLAUDE_SKILL_DIR}/../chess-play/scripts/chess_play.py" save-game <name> --json
```

Report the save name and current turn. Do not summarize the full move history unless the user asks.
