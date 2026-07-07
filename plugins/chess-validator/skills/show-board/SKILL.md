---
name: show-board
description: Render the current Chess Validator board and side to move. Use when the user invokes show-board or asks to see the current board, status, FEN, check state, last move, or game result.
---

# Show Board

Use the sibling script as the source of truth:

```bash
python3 "${CLAUDE_SKILL_DIR}/../chess-play/scripts/chess_play.py" show-board --json
```

Render `status.board`, side to move, check state, last move, and outcome when present. Do not include FEN unless the user asks for it.
