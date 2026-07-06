---
name: chess-play
description: Play against the agent or referee turn-by-turn chess directly inside Codex or Claude Code. Use when the user wants to start a chess game, play chess against the agent/LLM, render a chess board, validate whether a move is legal, apply a human or agent chess move, list legal moves, continue a saved chess position, or prevent LLM chess hallucinations such as illegal moves, lost board state, or invented pieces.
---

# Chess Play

Use the bundled script as the source of truth for board state and legal moves. Do not validate chess moves from memory.

The script is at `scripts/chess_play.py` inside this skill directory. In Codex, resolve `<skill-dir>` from this skill's source path before running commands; do not pass the angle-bracket placeholder literally.

```bash
python3 <skill-dir>/scripts/chess_play.py
```

In Claude Code skill content, `${CLAUDE_SKILL_DIR}` resolves to `<skill-dir>`.

Claude Code command form:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/chess_play.py"
```

Use `python3` on Unix/macOS. If `python3` is unavailable, use `python` or `py -3` with the same arguments.

The script stores game state in `.chess-validator-game.json` in the current working directory by default. Save slots live under `.chess-validator-saves/` by default. Use `--state <path>` or `--save-dir <path>` for parallel games. It accepts SAN (`e4`, `Nf3`, `O-O`, `Qxf7#`) and UCI (`e2e4`, `g1f3`, `e7e8q`) moves.

On first run, the script installs the Python `chess` package into a user-writable dependency cache if it is not already importable. Set `CHESS_VALIDATOR_DEPS` to choose that cache directory explicitly. This is local execution only; it does not use MCP or a server.

## Workflow

Use one-shot JSON commands by default because they work in both Codex and Claude Code:

Start or reset a game:

```bash
python3 <skill-dir>/scripts/chess_play.py new-game --force --json
```

Show the current board:

```bash
python3 <skill-dir>/scripts/chess_play.py show-board --json
```

Validate without changing state:

```bash
python3 <skill-dir>/scripts/chess_play.py validate "Nf3" --json
```

Apply a human move:

```bash
python3 <skill-dir>/scripts/chess_play.py move "e4" --by human --json
```

Build the minimal prompt for an LLM opponent:

```bash
python3 <skill-dir>/scripts/chess_play.py prompt --json
```

Apply the agent's selected move:

```bash
python3 <skill-dir>/scripts/chess_play.py move "c5" --by agent --json
```

List legal moves:

```bash
python3 <skill-dir>/scripts/chess_play.py legal-moves --json
```

Let the script choose and apply a simple legal agent move:

```bash
python3 <skill-dir>/scripts/chess_play.py agent-move --json
```

Save, load, or list saved game slots:

```bash
python3 <skill-dir>/scripts/chess_play.py save-game "default" --json
python3 <skill-dir>/scripts/chess_play.py load-game "default" --json
python3 <skill-dir>/scripts/chess_play.py list-saves --json
```

In Codex tool sessions, a persistent process can avoid repeated Python imports:

```bash
python3 <skill-dir>/scripts/chess_play.py serve
```

Then send JSON lines on stdin:

```json
{"cmd":"new-game"}
{"cmd":"move","move":"d4","by":"human"}
{"cmd":"save-game","name":"after-d4"}
{"cmd":"prompt"}
{"cmd":"move","move":"Nf6","by":"agent"}
{"cmd":"validate","move":"Bf4"}
{"cmd":"load-game","name":"after-d4"}
{"cmd":"show-board"}
```

Each input line returns one compact JSON line. Use `quit` to stop the process.

## Rules For Agents

- Default to **opponent mode** when the user says "play chess", "let's play", "I play White/Black", or sends chess moves after starting a game. In opponent mode, play the other side.
- Use **referee-only mode** only when the user explicitly asks to validate moves, render a board, analyze a position, or manage a two-human/agent-vs-agent game without the current agent playing.
- Before accepting any user move, run `move <move> --by human --json`.
- If `accepted` is `false`, tell the user the move was rejected, give the script's `reason`, and offer a few legal alternatives from `status.legal_moves`.
- If `accepted` is `true` in referee-only mode, relay the applied SAN/UCI move and render the returned board.
- If `accepted` is `true` in opponent mode and the game is not over, immediately choose and apply the agent's reply before responding to the user. Do not stop at "Black/White to move."
- To choose an agent reply, run `prompt --json`, choose exactly one UCI from the returned `legal_moves` using lightweight chess judgment, then run `move <uci> --by agent --json`.
- For game management, use `new-game --force --json`, `save-game <name> --json`, `load-game <name> --json`, or `list-saves --json` rather than manually editing state files.
- For display and move options, use `show-board --json` and `legal-moves --json`.
- Do not invent moves outside the legal list. If uncertain, choose a simple legal developing move from `legal_moves`.
- Do not send move history, rendered boards, skill files, or conversation context to the chess opponent unless the user explicitly asks for commentary. Chess is fully represented by the current FEN plus legal moves for this use case.
- For quick low-effort agent play, run `agent-move --json`; it chooses a random legal move and is not a chess engine.
- If the game is over, stop requesting moves and report the result from `status.outcome`.
- Use the board in `status.board` for display. Include turn, check status, last move, and outcome when relevant.

## Output Shape

Prefer concise chat output:

```text
Accepted: e4 (e2e4)
Agent: c5 (c7c5)

<board>

White to move.
```

For illegal moves:

```text
Illegal: wrong_turn: black to move
Legal options include: ...
```

Keep FEN available when useful for debugging, but do not make the user read FEN during normal play.

## Command Aliases

This plugin also includes thin command-style skills:

- `new-game`: start or reset a game.
- `save-game`: save the current game to a named slot.
- `load-game`: restore a named slot.
- `list-saves`: show available save slots.
- `show-board`: render the current board.
- `legal-moves`: list legal moves from the current position.
