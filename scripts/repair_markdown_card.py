"""Repair one damaged Markdown card after creating a database backup."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.db.database import DEFAULT_DB_PATH, backup_database
from src.services.card_service import get_card_by_id, update_card
from src.utils.markdown_normalizer import best_effort_repair_markdown


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Repair one card's Markdown content.")
    parser.add_argument("card_id", type=int, help="cards.id to repair")
    parser.add_argument(
        "--db-path",
        default=str(DEFAULT_DB_PATH),
        help="SQLite database path. Defaults to the app's real user database.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print repaired Markdown without writing to the database.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    db_path = Path(args.db_path).expanduser()
    card = get_card_by_id(args.card_id, db_path)
    if card is None:
        print(f"Card not found: {args.card_id}")
        return 1

    repaired = best_effort_repair_markdown(card.content)
    if args.dry_run:
        print(repaired)
        return 0

    backup_path = backup_database(db_path, reason=f"repair_markdown_card_{args.card_id}")
    update_card(int(card.id), db_path=db_path, content=repaired)
    print(f"Backup created: {backup_path}")
    print(f"Repaired card: {card.id} {card.title}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
