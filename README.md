# Chess Validator

Codex and Claude Code skills for playing or refereeing turn-by-turn chess with deterministic legal move validation.

The bundled `chess_play.py` script is the source of truth for board state, move parsing, legal move checks, board rendering, and compact LLM prompts. It accepts SAN and UCI moves and uses `python-chess` locally; no MCP server is required.

## Install

Codex:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R codex/skills/chess-play "${CODEX_HOME:-$HOME/.codex}/skills/"
```

Claude Code:

```bash
mkdir -p "$HOME/.claude/skills" "$HOME/.claude/agents"
cp -R claude/skills/chess-play "$HOME/.claude/skills/"
cp claude/agents/chess-opponent.md "$HOME/.claude/agents/"
```

## Usage

In Codex:

```text
Use $chess-play to start a legal chess game where I play White and Codex replies as Black after every legal move.
```

In Claude Code:

```bash
claude --agent chess-opponent --effort low
```

Then start with:

```text
let's play chess, I play White
```

## Direct CLI

```bash
python3 codex/skills/chess-play/scripts/chess_play.py new --force --json
python3 codex/skills/chess-play/scripts/chess_play.py move e4 --by human --json
python3 codex/skills/chess-play/scripts/chess_play.py prompt --json
python3 codex/skills/chess-play/scripts/chess_play.py move c5 --by agent --json
```

For Codex interactive play, the script also supports persistent JSONL mode:

```bash
python3 codex/skills/chess-play/scripts/chess_play.py serve
```

Send JSON lines such as:

```json
{"cmd":"new"}
{"cmd":"move","move":"d4","by":"human"}
{"cmd":"prompt"}
{"cmd":"move","move":"Nf6","by":"agent"}
{"cmd":"status"}
```
