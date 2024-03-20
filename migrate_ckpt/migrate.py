from collections.abc import MutableMapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
from importlib.util import module_from_spec, spec_from_file_location
from os import PathLike
from pathlib import Path
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
    for k, mig in reversed(list(enumerate(migrations))):
        if mig.name in done_migrations:
            return list(migrations[k + 1 :])
    return list(migrations)


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
) -> tuple[CkptType, Sequence[Migration]]:
    """
    Migrate checkpoint using provided migrations
    Args:
        ckpt: a MutableMapping
        migrations: a sequence of mappings
    """
    missing_migrations = get_missing_migrations(ckpt, migrations)
    for migration in missing_migrations:
        ckpt = migration.callback(deepcopy(ckpt))
        ckpt = _mark_ckpt(ckpt, migration)
    return ckpt, missing_migrations


def get_folder_migrations(path: str | PathLike) -> list[Migration]:
    migrations: list[Migration] = []

    for file in sorted(Path(path).iterdir()):
        if not file.is_file() and file.suffix != ".py":
            continue
        migration_spec = spec_from_file_location("handle", file)
        if migration_spec is None or migration_spec.loader is None:
            continue
        migration_mod = module_from_spec(migration_spec)
        migration_spec.loader.exec_module(migration_mod)
        migrations.append(
            Migration(
                name=file.stem,
                callback=migration_mod.handle,
            )
        )
    return migrations


def migrate_from_folder(
    ckpt: CkptType, path: str | PathLike
) -> tuple[CkptType, Sequence[Migration]]:
    return migrate_ckpt(ckpt, get_folder_migrations(path))
