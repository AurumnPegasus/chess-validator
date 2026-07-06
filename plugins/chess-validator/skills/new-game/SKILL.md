---
name: new-game
description: Start or reset a chess game with Chess Validator. Use when the user invokes a new-game command, wants a fresh board, wants to play White or Black from the start, or asks to restart the current chess game.
---

# New Game

Use the sibling chess script at `../chess-play/scripts/chess_play.py` as the source of truth. In Codex, resolve `<this-skill-dir>` from this skill's source path before running commands; do not pass the placeholder literally. In Claude Code, `${CLAUDE_SKILL_DIR}` is this skill directory.

Run:

```bash
python3 <this-skill-dir>/../chess-play/scripts/chess_play.py new-game --force --json
```

Claude Code form:

```bash
python3 "${CLAUDE_SKILL_DIR}/../chess-play/scripts/chess_play.py" new-game --force --json
```

Render the returned board. In Claude Code, command arguments are `$ARGUMENTS`; use `$ARGUMENTS` for color preferences such as "I play Black". If the user says they play Black, choose and apply one legal agent move for White before replying. Otherwise default to the user playing White and the agent playing Black.
