---
name: show-board
description: Render the current Chess Validator board and side to move. Use when the user invokes show-board or asks to see the current board, status, FEN, check state, last move, or game result.
---

# Show Board

Use the sibling chess script at `../chess-play/scripts/chess_play.py` as the source of truth. In Codex, resolve `<this-skill-dir>` from this skill's source path before running commands; do not pass the placeholder literally. In Claude Code, `${CLAUDE_SKILL_DIR}` is this skill directory. Use `python3` on Unix/macOS; if unavailable, use `python` or `py -3` with the same arguments.

Run:

```bash
python3 <this-skill-dir>/../chess-play/scripts/chess_play.py show-board --json
```

Claude Code form:

```bash
python3 "${CLAUDE_SKILL_DIR}/../chess-play/scripts/chess_play.py" show-board --json
```

Render `status.board`, side to move, check state, last move, and outcome when present. Do not include FEN unless the user asks for it.
