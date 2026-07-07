---
name: save-game
description: Save the current Chess Validator game position to a named save slot. Use when the user invokes save-game, asks to save the current chess game, checkpoint a position, or preserve a game before trying a line.
---

# Save Game

Use `$ARGUMENTS` as the save name. If it is empty, omit the name so the script uses `default`.

```bash
python3 "${CLAUDE_SKILL_DIR}/../chess-play/scripts/chess_play.py" save-game --json
python3 "${CLAUDE_SKILL_DIR}/../chess-play/scripts/chess_play.py" save-game "$ARGUMENTS" --json
```

Report the save name and current turn. Do not summarize the full move history unless the user asks.
