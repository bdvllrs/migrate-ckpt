from pathlib import Path
from typing import Any

from migrate_ckpt import ckpt_migration_key, migrate_from_folder


def test_execute_all_file_migrations():
    migration_folder = Path(__file__).parent / "migrations"
    ckpt: dict[str, Any] = {}
    new_ckpt, _ = migrate_from_folder(ckpt, migration_folder)
    assert "first_migration" in new_ckpt
    assert "second_migration" in new_ckpt
    assert new_ckpt["first_migration"] == "done long ago!"
    print(new_ckpt[ckpt_migration_key])
