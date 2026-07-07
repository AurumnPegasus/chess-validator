# Chess Validator

Play or referee turn-by-turn chess in Codex and Claude Code with deterministic legal move validation. The plugin keeps a local JSON board state, accepts SAN or UCI moves, and validates with [`python-chess`](https://python-chess.readthedocs.io/). It is not a chess engine and does not use MCP.

## Prerequisite

```bash
python3 -m pip install 'chess>=1.11,<2'
```

Install it into the Python visible to Codex or Claude Code. If your system Python blocks global installs, activate a virtualenv before launching the agent. Use `py -3` or `python` instead of `python3` when that is the Python command on your host.

## Install In Codex

```bash
codex plugin marketplace add AurumnPegasus/chess-validator
codex plugin add chess-validator@chess-validator
```

Start a new Codex session, then invoke the skill:

```text
Use $chess-validator:chess-play to start a legal chess game where I play White.
```

## Install In Claude Code

```text
/plugin marketplace add AurumnPegasus/chess-validator
/plugin install chess-validator@chess-validator
/reload-plugins
```

Then use the namespaced slash commands:

```text
/chess-validator:chess-play start a new game where I play White
```

## Commands

| Skill | Purpose |
| --- | --- |
| `chess-play` | Main play/referee workflow. |
| `new-game` | Start or reset the game. |
| `save-game [name]` | Save the current position. |
| `load-game [name]` | Restore a saved position. |
| `list-saves` | List saved positions. |
| `show-board` | Render board/status. |
| `legal-moves [square]` | List legal moves, optionally by source square. |

State lives in `.chess-validator-game.json`; saves live in `.chess-validator-saves/`.

## Direct Script

```bash
python3 plugins/chess-validator/skills/chess-play/scripts/chess_play.py new-game --force
python3 plugins/chess-validator/skills/chess-play/scripts/chess_play.py move e4 --by human
python3 plugins/chess-validator/skills/chess-play/scripts/chess_play.py prompt
python3 plugins/chess-validator/skills/chess-play/scripts/chess_play.py move c5 --by agent
python3 plugins/chess-validator/skills/chess-play/scripts/chess_play.py save-game after-e4
python3 plugins/chess-validator/skills/chess-play/scripts/chess_play.py load-game after-e4
```

Persistent JSONL mode:

```bash
python3 plugins/chess-validator/skills/chess-play/scripts/chess_play.py serve
```

Example lines:

```json
{"cmd":"new-game"}
{"cmd":"move","move":"d4","by":"human"}
{"cmd":"prompt"}
{"cmd":"move","move":"Nf6","by":"agent"}
{"cmd":"show-board"}
```

## Development

```bash
python3 -m pip install -r requirements.txt
python3 scripts/validate.py
claude plugin validate --strict .
```

Before changing public commands, update `README.md`, `CHANGELOG.md`, and both plugin manifest versions. Report security issues through GitHub Security Advisories.
