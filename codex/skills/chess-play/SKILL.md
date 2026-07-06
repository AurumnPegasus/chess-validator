---
name: chess-play
description: Play against Codex or referee turn-by-turn chess directly inside Codex chat or terminal. Use when the user wants to start a chess game, play chess against the agent/LLM/Codex, render a chess board, validate whether a move is legal, apply a human or agent chess move, list legal moves, continue a saved chess position, or prevent LLM chess hallucinations such as illegal moves, lost board state, or invented pieces.
---

# Chess Play

Use the bundled script as the source of truth for board state and legal moves. Do not validate chess moves from memory.

Script:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/chess-play/scripts/chess_play.py"
```

The script stores game state in `.codex-chess-game.json` in the current working directory by default. Use `--state <path>` for parallel games. It accepts SAN (`e4`, `Nf3`, `O-O`, `Qxf7#`) and UCI (`e2e4`, `g1f3`, `e7e8q`) moves.

On first run, the script installs the Python `chess` package into `scripts/.deps` if it is not already importable. This is local execution only; it does not use MCP or a server.

## Workflow

For a live game, prefer one persistent process so Python and `chess` are imported once:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/chess-play/scripts/chess_play.py" serve
```

When using Codex tools, start `serve` as an interactive/TTY session so stdin remains open for `write_stdin`.

Then send JSON lines on stdin:

```json
{"cmd":"new"}
{"cmd":"move","move":"d4","by":"human"}
{"cmd":"prompt"}
{"cmd":"legal"}
{"cmd":"move","move":"Nf6","by":"agent"}
{"cmd":"validate","move":"Bf4"}
{"cmd":"status"}
```

Each input line returns one compact JSON line. Use `quit` to stop the process.

Use one-shot commands only as a fallback or for quick checks:

Start or reset a game:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/chess-play/scripts/chess_play.py" new --force
```

Show the current board:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/chess-play/scripts/chess_play.py" status
```

Validate without changing state:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/chess-play/scripts/chess_play.py" validate "Nf3" --json
```

Apply a human move:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/chess-play/scripts/chess_play.py" move "e4" --by human --json
```

Apply an agent-selected move:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/chess-play/scripts/chess_play.py" move "c5" --by agent --json
```

Let the script choose and apply a simple legal agent move:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/chess-play/scripts/chess_play.py" agent-move --json
```

List legal moves:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/chess-play/scripts/chess_play.py" legal --json
```

Build the minimal prompt for an LLM opponent:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/chess-play/scripts/chess_play.py" prompt --json
```

## Rules For Codex

- For turn-by-turn play, start `serve` once and keep the session open; send JSON lines with `write_stdin` rather than spawning Python for every move.
- Default to **opponent mode** when the user says "play chess", "let's play", "I play White/Black", or sends chess moves after starting a game. In opponent mode, Codex plays the other side.
- Use **referee-only mode** only when the user explicitly asks to validate moves, render a board, analyze a position, or manage a two-human/agent-vs-agent game without Codex playing.
- Before accepting any user move, send `{"cmd":"move","move":"<move>","by":"human"}` or call `move <move> --by human --json` in fallback mode.
- If `accepted` is `false`, tell the user the move was rejected, give the script's `reason`, and offer a few legal alternatives from `status.legal_moves`.
- If `accepted` is `true` in referee-only mode, relay the applied SAN/UCI move and render the returned board.
- If `accepted` is `true` in opponent mode and the game is not over, immediately choose and apply Codex's reply before responding to the user. Do not stop at "Black/White to move."
- When an LLM opponent is playing a side, send `{"cmd":"prompt"}` and pass only the returned `prompt` string to the opponent. It contains FEN and legal moves only. Ask the opponent to return only UCI, then apply that UCI with `{"cmd":"move","move":"<uci>","by":"agent"}`.
- Do not send move history, rendered boards, skill files, or conversation context to the chess opponent unless the user explicitly asks for commentary. Chess is fully represented by the current FEN plus legal moves for this use case.
- When Codex itself is choosing without a subagent, send `{"cmd":"prompt"}`, choose one UCI from the returned legal moves/prompt, then send `{"cmd":"move","move":"<uci>","by":"agent"}`. Never invent a move outside the legal list.
- For quick low-effort agent play, send `{"cmd":"agent-move"}`; it chooses a random legal move and is not a chess engine.
- If the game is over, stop requesting moves and report the result from `status.outcome`.
- Use the board in `status.board` for display. Include turn, check status, last move, and outcome when relevant.

## Output Shape

Prefer concise chat output:

```text
Accepted: e4 (e2e4)
Codex: c5 (c7c5)

<board>

White to move.
```

For illegal moves:

```text
Illegal: wrong_turn: black to move
Legal options include: ... 
```

Keep FEN available when useful for debugging, but do not make the user read FEN during normal play.
