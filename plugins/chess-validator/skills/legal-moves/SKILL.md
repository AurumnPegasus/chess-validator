---
name: legal-moves
description: List legal chess moves for the current Chess Validator position. Use when the user invokes legal-moves or asks what moves are legal, whether a piece can move, or what options exist from the current board.
---

# Legal Moves

Use the sibling chess script at `../chess-play/scripts/chess_play.py` as the source of truth. In Codex, resolve `<this-skill-dir>` from this skill's source path before running commands; do not pass the placeholder literally. In Claude Code, `${CLAUDE_SKILL_DIR}` is this skill directory.

If the user supplies a square such as `e2` or `g8`, pass it with `--square`. In Claude Code, command arguments are `$ARGUMENTS`; use `$ARGUMENTS` as the optional square when it is non-empty. Otherwise list all legal moves.

Run:

```bash
python3 <this-skill-dir>/../chess-play/scripts/chess_play.py legal-moves --json
```

Claude Code form:

```bash
python3 "${CLAUDE_SKILL_DIR}/../chess-play/scripts/chess_play.py" legal-moves --json
```

Return a compact list of SAN moves with UCI in parentheses. If the list is long, group or truncate sensibly and offer to narrow by square.
