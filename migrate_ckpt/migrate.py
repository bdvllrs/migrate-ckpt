from collections.abc import MutableMapping, Sequence
from dataclasses import dataclass
from typing import Any, Callable, TypeAlias

ckpt_migration_key = "_migrate-ckpt-migrations"


class MissingMigrationFieldException(BaseException):
    pass


CkptType: TypeAlias = MutableMapping[str, Any]
MigrationCallback: TypeAlias = Callable[[CkptType], CkptType]


@dataclass
class Migration:
    name: str
    callback: MigrationCallback


def get_missing_migrations(
    ckpt: CkptType, migrations: Sequence[Migration]
) -> list[Migration]:
    """
    Get missing migrations from a checkpoint
    """
    if ckpt_migration_key not in ckpt:
        return list(migrations)
    done_migrations = ckpt[ckpt_migration_key]
    return [mig for mig in migrations if mig.name not in done_migrations]


def _mark_ckpt(ckpt: CkptType, migration: Migration) -> CkptType:
    """
    Add migration fields to ckpt
    """
    if ckpt_migration_key not in ckpt.keys():
        ckpt[ckpt_migration_key] = []
    ckpt[ckpt_migration_key].append(migration.name)
    return ckpt


def migrate_ckpt(
    ckpt: CkptType,
    migrations: Sequence[Migration],
) -> CkptType:
    """
    Migrate checkpoint using provided migrations
    Args:
        ckpt: a MutableMapping
        migrations: a sequence of mappings
    """
    missing_migrations = get_missing_migrations(ckpt, migrations)
    for migration in missing_migrations:
        ckpt = migration.callback(ckpt)
        ckpt = _mark_ckpt(ckpt, migration)
    return ckpt
