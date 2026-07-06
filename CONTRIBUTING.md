# Contributing

Keep changes small and testable. The plugin is intentionally a thin wrapper around `python-chess`, so avoid adding chess-engine search or custom legal-move logic.

Before opening a pull request, run:

```bash
python3 -m pip install -r requirements.txt
python3 scripts/validate.py
```

For changes to public commands, update `README.md`, `CHANGELOG.md`, and the plugin version in both plugin manifests.
