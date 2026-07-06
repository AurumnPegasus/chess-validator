#!/usr/bin/env python3
"""Tiny chess CLI: render, validate, and apply legal moves."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import random
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEPS = ROOT / ".deps"
DEFAULT_STATE = ".chess-validator-game.json"
DEFAULT_SAVE_DIR = ".chess-validator-saves"
SLOT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


def get_chess():
    if DEPS.exists():
        sys.path.insert(0, str(DEPS))
    try:
        import chess  # type: ignore
    except ModuleNotFoundError:
        DEPS.mkdir(exist_ok=True)
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--quiet", "--target", str(DEPS), "chess>=1.11,<2"]
        )
        sys.path.insert(0, str(DEPS))
        import chess  # type: ignore
    return chess


chess = get_chess()


def path(name: str | None) -> Path:
    return Path(name or DEFAULT_STATE).resolve()


def save_dir(name: str | None) -> Path:
    return Path(name or DEFAULT_SAVE_DIR).resolve()


def save_slot(directory: Path, name: str | None) -> Path:
    directory = Path(directory)
    slot = (name or "default").strip()
    if not SLOT_RE.fullmatch(slot):
        raise ValueError("save name must be 1-64 chars: letters, digits, dot, underscore, or hyphen")
    return directory / f"{slot}.json"


def load(state: Path):
    if not state.exists():
        board = chess.Board()
        save(state, board, [])
        return board, []
    data = json.loads(state.read_text())
    return chess.Board(data["fen"]), data.get("moves", [])


def save(state: Path, board, moves) -> None:
    state.parent.mkdir(parents=True, exist_ok=True)
    state.write_text(json.dumps({"fen": board.fen(), "moves": moves}, indent=2) + "\n")


def save_game(directory: Path, name: str | None, board, moves) -> dict:
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    target = save_slot(directory, name)
    payload = {
        "fen": board.fen(),
        "moves": moves,
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "format": "chess-validator.v1",
    }
    target.write_text(json.dumps(payload, indent=2) + "\n")
    return {"saved": True, "name": target.stem, "path": str(target), "status": status(board, moves)}


def load_game(state: Path, directory: Path, name: str | None):
    directory = Path(directory)
    source = save_slot(directory, name)
    if not source.exists():
        return {"loaded": False, "name": source.stem, "reason": "save not found", "path": str(source)}, None, None
    data = json.loads(source.read_text())
    board = chess.Board(data["fen"])
    moves = data.get("moves", [])
    save(state, board, moves)
    return {"loaded": True, "name": source.stem, "path": str(source), "status": status(board, moves)}, board, moves


def list_saves(directory: Path) -> dict:
    directory = Path(directory)
    saves = []
    if directory.exists():
        for item in sorted(directory.glob("*.json")):
            entry = {"name": item.stem, "path": str(item)}
            try:
                data = json.loads(item.read_text())
                entry["fen"] = data.get("fen")
                entry["saved_at"] = data.get("saved_at")
                entry["move_count"] = len(data.get("moves", []))
            except Exception as exc:
                entry["error"] = str(exc)
            saves.append(entry)
    return {"save_dir": str(directory), "saves": saves}


def parse(board, text: str):
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
    out = {
        "board": board_text(board),
        "fen": board.fen(),
        "turn": "white" if board.turn == chess.WHITE else "black",
        "check": board.is_check(),
        "game_over": board.is_game_over(claim_draw=True),
        "outcome": board.outcome(claim_draw=True).result() if board.outcome(claim_draw=True) else None,
        "last_move": moves[-1] if moves else None,
        "legal_move_count": board.legal_moves.count(),
    }
    if include_legal:
        out["legal_moves"] = legal_rows(board)
    return out


def print_status(board, moves) -> None:
    s = status(board, moves)
    print(s["board"])
    print()
    print(f"Turn: {s['turn']}")
    if s["last_move"]:
        print(f"Last move: {s['last_move']['san']} ({s['last_move']['uci']}) by {s['last_move']['by']}")
    print(f"Check: {'yes' if s['check'] else 'no'}")
    print(f"Legal moves: {s['legal_move_count']}")


def emit(obj, as_json: bool) -> None:
    print(json.dumps(obj, indent=2, sort_keys=True) if as_json else obj)


def run(cmd: str, board, moves, state: Path, **args):
    cmd = {"show-board": "status", "legal-moves": "legal"}.get(cmd, cmd)
    if cmd in {"new", "new-game"}:
        board, moves = chess.Board(), []
        save(state, board, moves)
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

    if cmd not in {"move", "validate"}:
        return {"error": f"unknown command: {cmd}"}, board, moves
    if not args.get("move"):
        return {"error": f"{cmd} requires a move"}, board, moves

    try:
        chosen = parse(board, args["move"])
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
    save(state, board, moves)
    return {"accepted": True, "applied": moves[-1], "status": status(board, moves)}, board, moves


def serve(state: Path, saves: Path) -> None:
    board, moves = load(state)
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


def main() -> None:
    as_json = "--json" in sys.argv[1:]
    sys.argv = [sys.argv[0], *[arg for arg in sys.argv[1:] if arg != "--json"]]
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
    save_parser = sub.add_parser("save-game")
    save_parser.add_argument("name", nargs="?", default="default")
    load_parser = sub.add_parser("load-game")
    load_parser.add_argument("name", nargs="?", default="default")
    sub.add_parser("list-saves")
    legal = sub.add_parser("legal")
    legal.add_argument("--square")
    legal_moves = sub.add_parser("legal-moves")
    legal_moves.add_argument("--square")
    validate = sub.add_parser("validate")
    validate.add_argument("move")
    move = sub.add_parser("move")
    move.add_argument("move")
    move.add_argument("--by", choices=["human", "agent"], default="human")
    agent = sub.add_parser("agent-move")
    agent.add_argument("--by", default="agent")
    args = parser.parse_args()
    args.json = as_json

    state = path(args.state)
    saves = save_dir(args.save_dir)
    if args.cmd == "serve":
        return serve(state, saves)
    if args.cmd in {"new", "new-game"}:
        if state.exists() and not args.force:
            raise SystemExit(f"{state} exists; use --force")
        out, board, moves = run(args.cmd, None, None, state)
        return emit(out, args.json) if args.json else print_status(board, moves)

    board, moves = load(state)
    opts = vars(args).copy()
    opts["save_dir"] = saves
    for key in ("cmd", "state", "json"):
        opts.pop(key, None)
    out, board, moves = run(args.cmd, board, moves, state, **opts)
    return emit(out, args.json) if args.json else print_status(board, moves)


if __name__ == "__main__":
    main()
