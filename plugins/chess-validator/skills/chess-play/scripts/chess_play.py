#!/usr/bin/env python3
"""Tiny chess CLI: render, validate, and apply legal moves."""

from __future__ import annotations

import argparse
import json
import random
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEPS = ROOT / ".deps"
DEFAULT_STATE = ".chess-validator-game.json"


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


def load(state: Path):
    if not state.exists():
        board = chess.Board()
        save(state, board, [])
        return board, []
    data = json.loads(state.read_text())
    return chess.Board(data["fen"]), data.get("moves", [])


def save(state: Path, board, moves) -> None:
    state.write_text(json.dumps({"fen": board.fen(), "moves": moves}, indent=2) + "\n")


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
    if cmd == "new":
        board, moves = chess.Board(), []
        save(state, board, moves)
        return status(board, moves), board, moves
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


def serve(state: Path) -> None:
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
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("serve")
    sub.add_parser("new").add_argument("--force", action="store_true")
    sub.add_parser("status").add_argument("--legal", action="store_true")
    sub.add_parser("prompt")
    legal = sub.add_parser("legal")
    legal.add_argument("--square")
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
    if args.cmd == "serve":
        return serve(state)
    if args.cmd == "new":
        if state.exists() and not args.force:
            raise SystemExit(f"{state} exists; use --force")
        out, board, moves = run("new", None, None, state)
        return emit(out, args.json) if args.json else print_status(board, moves)

    board, moves = load(state)
    opts = vars(args).copy()
    for key in ("cmd", "state", "json"):
        opts.pop(key, None)
    out, board, moves = run(args.cmd, board, moves, state, **opts)
    return emit(out, args.json) if args.json else print_status(board, moves)


if __name__ == "__main__":
    main()
