"""Command-line entry point for Linux."""

from __future__ import annotations

import argparse
import json
import platform

from .backend import LocalBackend
from .inventory import collect_inventory
from .service import serve


def main() -> None:
    parser = argparse.ArgumentParser(prog="logicasofia", description="LogicaSofia Linux AI gateway")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("inventory", help="Print read-only hardware inventory as JSON")
    server = commands.add_parser("serve", help="Start the localhost HTTP gateway")
    server.add_argument("--port", type=int, default=8765)
    server.add_argument("--backend-url", help="Existing LOCAL OpenAI-compatible server (example: http://127.0.0.1:8080)")
    args = parser.parse_args()
    if args.command == "inventory":
        print(json.dumps(collect_inventory(), ensure_ascii=False, indent=2))
    else:
        if platform.system() != "Linux":
            parser.error("LogicaSofia currently supports Linux hosts")
        try:
            backend = LocalBackend.from_url(args.backend_url) if args.backend_url else None
        except ValueError as exc:
            parser.error(str(exc))
        serve(port=args.port, backend=backend)


if __name__ == "__main__":
    main()
