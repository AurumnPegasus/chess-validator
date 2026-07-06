#!/usr/bin/env python3
"""Repository validation for the Chess Validator plugin."""

from __future__ import annotations

import json
import py_compile
import re
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "chess-validator"
SCRIPT = PLUGIN / "skills" / "chess-play" / "scripts" / "chess_play.py"


def read_json(path: Path) -> dict:
    with path.open() as handle:
        return json.load(handle)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def check_manifests() -> None:
    codex = read_json(PLUGIN / ".codex-plugin" / "plugin.json")
    claude = read_json(PLUGIN / ".claude-plugin" / "plugin.json")
    codex_market = read_json(ROOT / ".agents" / "plugins" / "marketplace.json")
    claude_market = read_json(ROOT / ".claude-plugin" / "marketplace.json")

    for manifest in (codex, claude):
        require(manifest["name"] == "chess-validator", "plugin name mismatch")
        require(re.fullmatch(r"\d+\.\d+\.\d+", manifest["version"]), "plugin version must be semver")
        require(manifest["description"], "plugin description is required")

    require(codex["version"] == claude["version"], "Codex and Claude plugin versions differ")
    require(codex_market["plugins"][0]["name"] == "chess-validator", "Codex marketplace missing plugin")
    require(claude_market["plugins"][0]["version"] == claude["version"], "Claude marketplace version mismatch")


def check_skills() -> None:
    skills_dir = PLUGIN / "skills"
    expected = {"chess-play", "new-game", "save-game", "load-game", "list-saves", "show-board", "legal-moves"}
    found = {path.parent.name for path in skills_dir.glob("*/SKILL.md")}
    require(expected <= found, f"missing skills: {sorted(expected - found)}")

    for skill in skills_dir.glob("*/SKILL.md"):
        text = skill.read_text()
        require(text.startswith("---\n"), f"{skill} missing frontmatter")
        frontmatter = text.split("---", 2)[1]
        require("description:" in frontmatter, f"{skill} missing description")


def run_json(*args: str) -> dict:
    output = subprocess.check_output([sys.executable, str(SCRIPT), *args, "--json"], text=True)
    return json.loads(output)


def check_script() -> None:
    py_compile.compile(str(SCRIPT), doraise=True)

    with tempfile.TemporaryDirectory(prefix="chess-validator-test-") as tmp:
        tmp_path = Path(tmp)
        state = tmp_path / "game.json"
        saves = tmp_path / "saves"

        def call(*args: str) -> dict:
            return run_json("--state", str(state), "--save-dir", str(saves), *args)

        new = call("new-game", "--force")
        require(new["turn"] == "white", "new-game did not start with white to move")

        initial = call("save-game", "initial")
        require(initial["saved"] and initial["status"]["last_move"] is None, "initial save failed")

        move = call("move", "e4", "--by", "human")
        require(move["accepted"] and move["status"]["turn"] == "black", "human e4 was not applied")

        saved = call("save-game", "after-e4")
        require(saved["saved"] and saved["name"] == "after-e4", "save-game failed")

        listed = call("list-saves")
        require({item["name"] for item in listed["saves"]} == {"after-e4", "initial"}, "list-saves failed")

        board = call("show-board")
        require(board["last_move"]["san"] == "e4", "show-board alias failed")

        legal_alias = call("legal-moves", "--square", "c7")
        require(any(row["uci"] == "c7c5" for row in legal_alias["legal_moves"]), "legal-moves alias failed")

        reply = call("move", "c5", "--by", "agent")
        require(reply["accepted"] and reply["status"]["turn"] == "white", "agent c5 was not applied")

        loaded_initial = call("load-game", "initial")
        require(
            loaded_initial["loaded"] and loaded_initial["status"]["last_move"] is None,
            "load-game kept stale move history for empty save",
        )

        loaded = call("load-game", "after-e4")
        require(loaded["loaded"] and loaded["status"]["turn"] == "black", "load-game failed")

        legal = call("legal")
        require(any(row["uci"] == "c7c5" for row in legal["legal_moves"]), "legal moves missing c7c5 after load")


def main() -> None:
    check_manifests()
    check_skills()
    check_script()
    print("validation passed")


if __name__ == "__main__":
    main()
