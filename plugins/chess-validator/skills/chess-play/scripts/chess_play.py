#!/usr/bin/env python3
"""Chess CLI: render, validate, save, and apply legal moves."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
import random
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote, unquote

APP_NAME = "chess-validator"
CHESS_DEPENDENCY = "chess>=1.11,<2"
DEFAULT_STATE = ".chess-validator-game.json"
DEFAULT_SAVE_DIR = ".chess-validator-saves"
MAX_SAVE_NAME = 64
COMMAND_ALIASES = {"show-board": "status", "legal-moves": "legal"}

chess = None


# Dependency loading

def dependency_cache() -> Path:
    override = os.environ.get("CHESS_VALIDATOR_DEPS")
    if override:
        return Path(override).expanduser()

    if os.name == "nt":
        root = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
        base = Path(root) if root else Path.home() / "AppData" / "Local"
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Caches"
    else:
        base = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")

    py_version = f"py{sys.version_info.major}.{sys.version_info.minor}"
    return base / APP_NAME / "deps" / py_version


def import_chess_module():
    try:
        import chess as chess_module  # type: ignore

        return chess_module
    except ModuleNotFoundError:
        pass

    deps = dependency_cache()
    if deps.exists():
        sys.path.insert(0, str(deps))
        try:
            import chess as chess_module  # type: ignore

            return chess_module
        except ModuleNotFoundError:
            pass

    try:
        deps.mkdir(parents=True, exist_ok=True)
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--quiet",
                "--target",
                str(deps),
                CHESS_DEPENDENCY,
            ]
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RuntimeError(
            f"{CHESS_DEPENDENCY} is required. Install it with pip or set "
            f"CHESS_VALIDATOR_DEPS to a writable dependency directory. Bootstrap failed: {exc}"
        ) from exc

    sys.path.insert(0, str(deps))
    try:
        import chess as chess_module  # type: ignore

        return chess_module
    except ModuleNotFoundError as exc:
        raise RuntimeError(f"{CHESS_DEPENDENCY} installed but could not be imported from {deps}") from exc


def ensure_chess():
    global chess
    if chess is None:
        chess = import_chess_module()
    return chess


# Paths and persistence

def path(name: str | None) -> Path:
    return Path(name or DEFAULT_STATE).expanduser().resolve()


def save_dir(name: str | None) -> Path:
    return Path(name or DEFAULT_SAVE_DIR).expanduser().resolve()


def save_name(raw) -> str:
    if isinstance(raw, (list, tuple)):
        raw = " ".join(str(part) for part in raw) if raw else None
    name = (str(raw) if raw is not None else "default").strip()
    if not name:
        raise ValueError("save name cannot be empty")
    if len(name) > MAX_SAVE_NAME:
        raise ValueError(f"save name must be {MAX_SAVE_NAME} characters or fewer")
    return name


def save_slot(directory: Path, raw_name) -> tuple[Path, str]:
    name = save_name(raw_name)
    filename = quote(name, safe="._-")
    return Path(directory) / f"{filename}.json", name


def load_state(state: Path):
    if not state.exists():
        board = chess.Board()
        save_state(state, board, [])
        return board, []

    try:
        data = json.loads(state.read_text())
        return chess.Board(data["fen"]), data.get("moves", [])
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError(f"could not load state {state}: {exc}") from exc


def save_state(state: Path, board, moves) -> None:
    state.parent.mkdir(parents=True, exist_ok=True)
    state.write_text(json.dumps({"fen": board.fen(), "moves": moves}, indent=2) + "\n")


def save_game(directory: Path, raw_name, board, moves) -> dict:
    try:
        target, name = save_slot(directory, raw_name)
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "format": "chess-validator.v1",
            "name": name,
            "fen": board.fen(),
            "moves": moves,
            "saved_at": datetime.now(timezone.utc).isoformat(),
        }
        target.write_text(json.dumps(payload, indent=2) + "\n")
        return {"saved": True, "name": name, "path": str(target), "status": status(board, moves)}
    except (OSError, ValueError) as exc:
        return {"saved": False, "reason": str(exc), "save_dir": str(directory), "status": status(board, moves)}


def load_game(state: Path, directory: Path, raw_name):
    try:
        source, name = save_slot(directory, raw_name)
    except ValueError as exc:
        return {"loaded": False, "reason": str(exc), "save_dir": str(directory)}, None, None

    if not source.exists():
        return {"loaded": False, "name": name, "reason": "save not found", "path": str(source)}, None, None

    try:
        data = json.loads(source.read_text())
        board = chess.Board(data["fen"])
        moves = data.get("moves", [])
        save_state(state, board, moves)
        return {"loaded": True, "name": data.get("name", name), "path": str(source), "status": status(board, moves)}, board, moves
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        return {"loaded": False, "name": name, "reason": f"could not load save: {exc}", "path": str(source)}, None, None


def list_saves(directory: Path) -> dict:
    saves = []
    try:
        items = sorted(Path(directory).glob("*.json")) if Path(directory).exists() else []
    except OSError as exc:
        return {"save_dir": str(directory), "saves": [], "error": str(exc)}

    for item in items:
        entry = {"name": unquote(item.stem), "path": str(item)}
        try:
            data = json.loads(item.read_text())
            entry["name"] = data.get("name", entry["name"])
            entry["fen"] = data.get("fen")
            entry["saved_at"] = data.get("saved_at")
            entry["move_count"] = len(data.get("moves", []))
        except Exception as exc:
            entry["error"] = str(exc)
        saves.append(entry)
    return {"save_dir": str(directory), "saves": saves}


# Board rendering and move parsing

def parse_move(board, text: str):
    text = text.strip().replace("0-0-0", "O-O-O").replace("0-0", "O-O")
    try:
        return chess.Move.from_uci(text.lower())
    except ValueError:
        return board.parse_san(text)


def board_text(board) -> str:
    rows = ["    a b c d e f g h", "  +-----------------+"]
    for rank in range(7, -1, -1):
        cells = []
        for file in range(8):
            piece = board.piece_at(chess.square(file, rank))
            cells.append(piece.symbol() if piece else ".")
        rows.append(f"{rank + 1} | {' '.join(cells)} | {rank + 1}")
    rows += ["  +-----------------+", "    a b c d e f g h"]
    return "\n".join(rows)


def legal_rows(board):
    return [{"san": board.san(move), "uci": move.uci()} for move in board.legal_moves]


def opponent_prompt(board):
    moves = legal_rows(board)
    lines = [
        f"You are {'White' if board.turn == chess.WHITE else 'Black'} in a chess game.",
        f"FEN: {board.fen()}",
        "Legal moves:",
        *[f"{row['uci']} {row['san']}" for row in moves],
        "Choose one legal move. Return only UCI, no explanation.",
    ]
    return {"fen": board.fen(), "legal_moves": moves, "prompt": "\n".join(lines)}


def status(board, moves, include_legal=False):
    outcome = board.outcome(claim_draw=True)
    out = {
        "board": board_text(board),
        "fen": board.fen(),
        "turn": "white" if board.turn == chess.WHITE else "black",
        "check": board.is_check(),
        "game_over": board.is_game_over(claim_draw=True),
        "outcome": outcome.result() if outcome else None,
        "last_move": moves[-1] if moves else None,
        "legal_move_count": board.legal_moves.count(),
    }
    if include_legal:
        out["legal_moves"] = legal_rows(board)
    return out


# Command handling

def run(cmd: str, board, moves, state: Path, **args):
    cmd = COMMAND_ALIASES.get(cmd, cmd)

    if cmd in {"new", "new-game"}:
        board, moves = chess.Board(), []
        save_state(state, board, moves)
        return status(board, moves), board, moves

    if cmd == "save-game":
        return save_game(args["save_dir"], args.get("name"), board, moves), board, moves

    if cmd == "load-game":
        out, loaded_board, loaded_moves = load_game(state, args["save_dir"], args.get("name"))
        return (
            out,
            loaded_board if loaded_board is not None else board,
            loaded_moves if loaded_moves is not None else moves,
        )

    if cmd == "list-saves":
        return list_saves(args["save_dir"]), board, moves

    if cmd == "status":
        return status(board, moves, args.get("legal", False)), board, moves

    if cmd == "legal":
        rows = legal_rows(board)
        if args.get("square"):
            rows = [row for row in rows if row["uci"].startswith(args["square"])]
        return {"legal_moves": rows, "turn": status(board, moves)["turn"]}, board, moves

    if cmd == "prompt":
        return opponent_prompt(board), board, moves

    if cmd == "agent-move":
        legals = list(board.legal_moves)
        if not legals:
            return {"accepted": False, "reason": "game over", "status": status(board, moves)}, board, moves
        args["move"] = random.choice(legals).uci()
        cmd = "move"

    return move_or_validate(cmd, board, moves, state, **args)


def move_or_validate(cmd: str, board, moves, state: Path, **args):
    if cmd not in {"move", "validate"}:
        return {"error": f"unknown command: {cmd}"}, board, moves
    if not args.get("move"):
        return {"error": f"{cmd} requires a move"}, board, moves

    try:
        chosen = parse_move(board, args["move"])
    except ValueError as exc:
        chosen, reason = None, str(exc)

    if cmd == "validate":
        ok = chosen in board.legal_moves
        out = {"legal": ok, "move": args["move"], "status": status(board, moves, not ok)}
        if ok:
            out["san"], out["uci"] = board.san(chosen), chosen.uci()
        else:
            out["reason"] = locals().get("reason", "illegal")
        return out, board, moves

    if chosen not in board.legal_moves:
        return {
            "accepted": False,
            "move": args["move"],
            "reason": locals().get("reason", "illegal"),
            "status": status(board, moves, True),
        }, board, moves

    san = board.san(chosen)
    board.push(chosen)
    moves.append({"by": args.get("by", "human"), "san": san, "uci": chosen.uci()})
    save_state(state, board, moves)
    return {"accepted": True, "applied": moves[-1], "status": status(board, moves)}, board, moves


# Output

def emit(obj, as_json: bool) -> None:
    print(json.dumps(obj, indent=2, sort_keys=True) if as_json else obj)


def fail(message: str, as_json: bool) -> int:
    if as_json:
        emit({"error": message}, True)
    else:
        print(message, file=sys.stderr)
    return 1


def print_status(board, moves) -> None:
    s = status(board, moves)
    print(s["board"])
    print()
    print(f"Turn: {s['turn']}")
    if s["last_move"]:
        print(f"Last move: {s['last_move']['san']} ({s['last_move']['uci']}) by {s['last_move']['by']}")
    print(f"Check: {'yes' if s['check'] else 'no'}")
    print(f"Legal moves: {s['legal_move_count']}")


def print_human(cmd: str, out: dict, board, moves) -> None:
    cmd = COMMAND_ALIASES.get(cmd, cmd)

    if "error" in out:
        print(out["error"], file=sys.stderr)
        return

    if cmd == "list-saves":
        for item in out.get("saves", []):
            suffix = f" ({item.get('move_count', 0)} moves)" if "move_count" in item else ""
            print(f"{item['name']}{suffix}")
        if not out.get("saves"):
            print("No saves.")
        return

    if cmd == "save-game" and not out.get("saved", False):
        print(f"Save failed: {out.get('reason', 'unknown error')}", file=sys.stderr)
        return

    if cmd == "save-game":
        print(f"Saved: {out['name']}")
    elif cmd == "load-game" and not out.get("loaded", False):
        print(f"Load failed: {out.get('reason', 'unknown error')}", file=sys.stderr)
        return
    elif cmd == "load-game":
        print(f"Loaded: {out['name']}")

    print_status(board, moves)


# CLI and JSONL server

def serve(state: Path, saves: Path) -> int:
    try:
        board, moves = load_state(state)
    except Exception as exc:
        emit({"error": str(exc)}, True)
        return 1

    print(json.dumps({"ready": True, "status": status(board, moves)}), flush=True)
    restore = None
    if sys.stdin.isatty():
        try:
            import termios

            restore = termios.tcgetattr(sys.stdin)
            attrs = restore[:]
            attrs[3] &= ~termios.ECHO
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, attrs)
        except Exception:
            restore = None

    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            if line in {"quit", "exit"}:
                break
            try:
                data = json.loads(line)
                data.setdefault("save_dir", saves)
                out, board, moves = run(data.pop("cmd"), board, moves, state, **data)
            except Exception as exc:
                out = {"error": str(exc)}
            print(json.dumps(out, sort_keys=True), flush=True)
    finally:
        if restore is not None:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, restore)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", default=DEFAULT_STATE)
    parser.add_argument("--save-dir", default=DEFAULT_SAVE_DIR)
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("serve")
    for name in ("new", "new-game"):
        sub.add_parser(name).add_argument("--force", action="store_true")

    sub.add_parser("status").add_argument("--legal", action="store_true")
    sub.add_parser("show-board").add_argument("--legal", action="store_true")
    sub.add_parser("prompt")

    for name in ("save-game", "load-game"):
        parser_for_save = sub.add_parser(name)
        parser_for_save.add_argument("name", nargs="*", default=["default"])

    sub.add_parser("list-saves")

    for name in ("legal", "legal-moves"):
        legal = sub.add_parser(name)
        legal.add_argument("--square")

    validate = sub.add_parser("validate")
    validate.add_argument("move")

    move = sub.add_parser("move")
    move.add_argument("move")
    move.add_argument("--by", choices=["human", "agent"], default="human")

    agent = sub.add_parser("agent-move")
    agent.add_argument("--by", default="agent")
    return parser


def parse_args(argv: list[str]) -> argparse.Namespace:
    as_json = "--json" in argv
    argv = [arg for arg in argv if arg != "--json"]
    args = build_parser().parse_args(argv)
    args.json = as_json
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    as_json = args.json or args.cmd == "serve"

    try:
        ensure_chess()
    except RuntimeError as exc:
        return fail(str(exc), as_json)

    state = path(args.state)
    saves = save_dir(args.save_dir)

    if args.cmd == "serve":
        return serve(state, saves)

    if args.cmd in {"new", "new-game"} and state.exists() and not args.force:
        return fail(f"{state} exists; use --force", args.json)

    try:
        if args.cmd in {"new", "new-game"}:
            out, board, moves = run(args.cmd, None, None, state)
        else:
            board, moves = load_state(state)
            opts = vars(args).copy()
            opts["save_dir"] = saves
            for key in ("cmd", "state", "json"):
                opts.pop(key, None)
            out, board, moves = run(args.cmd, board, moves, state, **opts)
    except Exception as exc:
        return fail(str(exc), args.json)

    if args.json:
        emit(out, True)
    else:
        print_human(args.cmd, out, board, moves)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
