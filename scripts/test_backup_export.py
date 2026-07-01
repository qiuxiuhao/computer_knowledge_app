"""Manual smoke test for database backup and Markdown export."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.db.database import initialize_database
from src.services.card_service import create_card
from src.services.data_safety_service import (
    create_manual_backup,
    export_formal_cards_to_markdown,
)


def main() -> int:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        db_path = root / "test_knowledge.db"
        backup_dir = root / "backups"
        export_dir = root / "exports"

        initialize_database(db_path)
        create_card(
            title="备份与导出测试",
            scenario="知识点",
            category="Python",
            tags="SQLite, Markdown",
            summary="验证数据库备份和正式卡片 Markdown 导出。",
            content="# 测试正文\n\n- 这是一张正式知识卡片。",
            db_path=db_path,
        )
        create_card(title="草稿不导出", is_draft=1, db_path=db_path)

        backup_path = create_manual_backup(db_path=db_path, backup_dir=backup_dir)
        exported_paths = export_formal_cards_to_markdown(export_dir, db_path=db_path)

        print(f"database: {db_path}")
        print(f"backup: {backup_path}")
        print("exports:")
        for path in exported_paths:
            print(f"- {path}")

        assert backup_path.exists()
        assert len(exported_paths) == 1
        assert exported_paths[0].read_text(encoding="utf-8").startswith("# 备份与导出测试")

    print("Backup and Markdown export smoke test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
