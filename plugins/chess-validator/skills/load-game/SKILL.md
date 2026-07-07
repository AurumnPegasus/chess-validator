---
name: load-game
description: Load a named Chess Validator save slot into the current game. Use when the user invokes load-game, asks to restore a chess game, continue from a saved position, or return to a checkpoint.
---

# Load Game

Use `$ARGUMENTS` as the save name. If it is empty, omit the name so the script uses `default`.

```bash
python3 "${CLAUDE_SKILL_DIR}/../chess-play/scripts/chess_play.py" load-game --json
python3 "${CLAUDE_SKILL_DIR}/../chess-play/scripts/chess_play.py" load-game "$ARGUMENTS" --json
```

If `loaded` is false, report the reason and suggest `list-saves`. If loaded, render the board, last move, and side to move.
