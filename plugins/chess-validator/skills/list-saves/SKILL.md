---
name: list-saves
description: List available Chess Validator save slots. Use when the user invokes list-saves or asks what saved chess games, checkpoints, or positions are available.
---

# List Saves

Use the sibling script as the source of truth:

```bash
python3 "${CLAUDE_SKILL_DIR}/../chess-play/scripts/chess_play.py" list-saves --json
```

Show save names, move counts, and saved timestamps when present. Keep the output compact.
