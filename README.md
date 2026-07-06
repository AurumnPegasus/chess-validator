# Chess Validator

Play or referee turn-by-turn chess in Codex and Claude Code with deterministic legal move validation.

Chess Validator keeps the board in a local JSON state file, renders the board, accepts SAN or UCI moves, and validates every move through [`python-chess`](https://python-chess.readthedocs.io/). It is not a chess engine and it does not run an MCP server. The aim is to stop LLM chess hallucinations while still letting the model act as the opponent.

## Install In Codex

Codex distributes reusable skills through plugins and marketplaces:

```bash
codex plugin marketplace add AurumnPegasus/chess-validator
codex plugin add chess-validator@chess-validator
```

Start a new Codex session after installation. Invoke the skills explicitly with the skill picker or a `$` mention:

```text
Use $chess-validator:chess-play to start a legal chess game where I play White.
```

Codex custom slash prompts are deprecated, so the command-style features ship as namespaced skills rather than Codex prompt files.

## Install In Claude Code

Claude Code plugin skills are available as namespaced slash commands:

```text
/plugin marketplace add AurumnPegasus/chess-validator
/plugin install chess-validator@chess-validator
/reload-plugins
```

Then start a game:

```text
/chess-validator:chess-play start a new game where I play White
```

The same flow is available from the shell:

```bash
claude plugin marketplace add AurumnPegasus/chess-validator
claude plugin install chess-validator@chess-validator
```

## Commands

Use these as Claude slash commands, for example `/chess-validator:new-game`, or as Codex skill mentions, for example `$chess-validator:new-game`.

| Skill | Purpose |
| --- | --- |
| `chess-play` | Main play/referee workflow. Use this for normal games against the agent. |
| `new-game` | Start or reset the current game. |
| `save-game [name]` | Save the current position to a named slot. |
| `load-game [name]` | Restore a saved slot into the current game. |
| `list-saves` | List saved slots. |
| `show-board` | Render the current board and status. |
| `legal-moves [square]` | List legal moves, optionally filtered by a source square such as `e2`. |

Default state is stored in `.chess-validator-game.json`. Save slots are stored in `.chess-validator-saves/`. Both are ignored by git.

## Direct Script

The bundled script is the source of truth and can be run directly from a checkout:

```bash
python3 plugins/chess-validator/skills/chess-play/scripts/chess_play.py new-game --force --json
python3 plugins/chess-validator/skills/chess-play/scripts/chess_play.py move e4 --by human --json
python3 plugins/chess-validator/skills/chess-play/scripts/chess_play.py prompt --json
python3 plugins/chess-validator/skills/chess-play/scripts/chess_play.py move c5 --by agent --json
python3 plugins/chess-validator/skills/chess-play/scripts/chess_play.py save-game after-e4 --json
python3 plugins/chess-validator/skills/chess-play/scripts/chess_play.py load-game after-e4 --json
```

Use persistent JSONL mode when you want to avoid repeated Python process/import startup:

```bash
python3 plugins/chess-validator/skills/chess-play/scripts/chess_play.py serve
```

Use `python3` on Unix/macOS. On Windows or hosts without `python3`, use `py -3` or `python` with the same arguments.

Example input lines:

```json
{"cmd":"new-game"}
{"cmd":"move","move":"d4","by":"human"}
{"cmd":"save-game","name":"after-d4"}
{"cmd":"prompt"}
{"cmd":"move","move":"Nf6","by":"agent"}
{"cmd":"show-board"}
```

On first run, if `chess` is not importable, the script installs `chess>=1.11,<2` into a user-writable cache. Set `CHESS_VALIDATOR_DEPS=/path/to/deps` to choose the dependency cache directory explicitly.

## Development

Install dependencies and run the repository smoke checks:

```bash
python3 -m pip install -r requirements.txt
python3 scripts/validate.py
```

Additional plugin checks:

```bash
python3 /path/to/skill-creator/scripts/quick_validate.py plugins/chess-validator/skills/chess-play
python3 /path/to/plugin-creator/scripts/validate_plugin.py plugins/chess-validator
claude plugin validate --strict .
```

For local marketplace testing:

```bash
codex plugin marketplace add .
codex plugin add chess-validator@chess-validator
claude --plugin-dir ./plugins/chess-validator
```
