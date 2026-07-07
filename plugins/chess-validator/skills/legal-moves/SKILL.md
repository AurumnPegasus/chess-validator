---
name: legal-moves
description: List legal chess moves for the current Chess Validator position. Use when the user invokes legal-moves or asks what moves are legal, whether a piece can move, or what options exist from the current board.
---

# Legal Moves

Use `$ARGUMENTS` as an optional source square such as `e2` or `g8`. Run the sibling script:

```bash
python3 "${CLAUDE_SKILL_DIR}/../chess-play/scripts/chess_play.py" legal-moves --square "$ARGUMENTS" --json
```

Return a compact list of SAN moves with UCI in parentheses. If the list is long, group or truncate sensibly and offer to narrow by square.
