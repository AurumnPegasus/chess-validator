# Security Policy

Chess Validator is a local plugin. It does not run a network service and does not use MCP.

The bundled Python script installs `python-chess` into a user-writable dependency cache only when the package is not already importable. Set `CHESS_VALIDATOR_DEPS` to choose the cache directory explicitly. Review `requirements.txt` and the script before installing from an untrusted fork.

Report security issues through GitHub Security Advisories for this repository, or open a private report with enough detail to reproduce the issue.
