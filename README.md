# Chess Validator

Codex and Claude Code plugin for playing or refereeing turn-by-turn chess with deterministic legal move validation.

The bundled `chess_play.py` script is the source of truth for board state, move parsing, legal move checks, board rendering, and compact LLM prompts. It accepts SAN and UCI moves and uses `python-chess` locally; no MCP server is required.

## Install In Codex

Codex distributes reusable skills through plugins and marketplaces. Add this repository as a marketplace, then install the plugin:

```bash
codex plugin marketplace add AurumnPegasus/chess-validator
codex plugin add chess-validator@chess-validator
```

Start a new Codex thread after installation. Invoke the plugin or its bundled skill from the prompt:

```text
Use the chess-validator chess-play skill to start a legal chess game where I play White and the agent replies as Black.
```

During local development, load the repository checkout itself as a marketplace:

```bash
codex plugin marketplace add .
codex plugin add chess-validator@chess-validator
```

## Install In Claude Code

Claude Code also installs shared skills through plugin marketplaces. Add this repository as a marketplace, then install the plugin:

```bash
claude plugin marketplace add AurumnPegasus/chess-validator
claude plugin install chess-validator@chess-validator
```

Restart or reload plugins, then invoke the namespaced skill:

```text
/chess-validator:chess-play start a new game where I play White
```

For local development, test without installing:

```bash
claude --plugin-dir ./plugins/chess-validator
```

## Direct Script

The script can still be run directly from a checkout for development and smoke tests:

```bash
python3 plugins/chess-validator/skills/chess-play/scripts/chess_play.py new --force --json
python3 plugins/chess-validator/skills/chess-play/scripts/chess_play.py move e4 --by human --json
python3 plugins/chess-validator/skills/chess-play/scripts/chess_play.py prompt --json
python3 plugins/chess-validator/skills/chess-play/scripts/chess_play.py move c5 --by agent --json
```

It also supports persistent JSONL mode:

```bash
python3 plugins/chess-validator/skills/chess-play/scripts/chess_play.py serve
```

Send JSON lines such as:

```json
{"cmd":"new"}
{"cmd":"move","move":"d4","by":"human"}
{"cmd":"prompt"}
{"cmd":"move","move":"Nf6","by":"agent"}
{"cmd":"status"}
```
