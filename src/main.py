"""Application entry point for the PySide6 desktop UI."""

from __future__ import annotations

import argparse
import sys

from PySide6.QtWidgets import QApplication

from src.ui.main_window import MainWindow


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Personal Computer Knowledge Base")
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Create the window and exit without starting the event loop.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    app = QApplication(sys.argv)
    app.setApplicationName("个人计算机知识库")

    window = MainWindow()
    window.show()

    if args.smoke_test:
        app.processEvents()
        print("PySide6 UI smoke test passed.")
        window.close()
        return 0

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
