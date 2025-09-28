import argparse
import os
import sys

from infrastructure.parser import parse_signals
from ui.app import SignalsViewerApp


def main() -> None:
    """
    Entry point for Django Signals Explorer.
    Parses arguments, validates project root, and launches the application.
    """
    parser = argparse.ArgumentParser(description="Django Signals Explorer")
    parser.add_argument(
        "--project-root",
        type=str,
        required=True,
        help="Root directory of your Django project",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.project_root):
        print(f"Error: {args.project_root} is not a valid directory.")
        sys.exit(1)

    signals = parse_signals(args.project_root)
    app = SignalsViewerApp(signals)
    sys.exit(app.run())


if __name__ == "__main__":
    main()
