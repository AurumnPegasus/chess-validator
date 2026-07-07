---
name: new-game
description: Start or reset a chess game with Chess Validator. Use when the user invokes a new-game command, wants a fresh board, wants to play White or Black from the start, or asks to restart the current chess game.
---

# New Game

Use the sibling script as the source of truth. In Claude Code run:

```bash
python3 "${CLAUDE_SKILL_DIR}/../chess-play/scripts/chess_play.py" new-game --force --json
```

Render the returned board. In Claude Code, command arguments are `$ARGUMENTS`; use `$ARGUMENTS` for color preferences such as "I play Black". If the user says they play Black, choose and apply one legal agent move for White before replying. Otherwise default to the user playing White and the agent playing Black.
