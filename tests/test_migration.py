from typing import Any

from migrate_ckpt import Migration, ckpt_migration_key, migrate_ckpt


def identity_callback(x):
    return x


def add_field_migration_callback(x):
    x["test"] = "ok"
    return x


def update_test_callback(x):
    assert "test" in x
    x["test"] = "nok"
    return x


blank_migration = Migration(name="blank", callback=identity_callback)
blank2_migration = Migration(name="blank2", callback=identity_callback)
add_field_migration = Migration(name="add_field", callback=add_field_migration_callback)
update_test_migration = Migration(name="update_test", callback=update_test_callback)


def test_missing_fields():
    ckpt: dict[str, Any] = {}
    new_ckpt, _ = migrate_ckpt(ckpt, [blank_migration])
    assert ckpt_migration_key in new_ckpt
    assert isinstance(new_ckpt[ckpt_migration_key], list)
    assert len(new_ckpt[ckpt_migration_key]) == 1
    assert new_ckpt[ckpt_migration_key][0] == "blank"


def test_missing_one_migration():
    ckpt, _ = migrate_ckpt({}, [blank_migration])
    new_ckpt, _ = migrate_ckpt(ckpt, [blank2_migration])
    assert new_ckpt[ckpt_migration_key][1] == "blank2"


def test_execute_migration():
    ckpt, _ = migrate_ckpt(
        {},
        [add_field_migration],
    )
    assert "test" in ckpt
    assert ckpt["test"] == "ok"


def test_execute_related_migrations():
    ckpt, _ = migrate_ckpt(
        {},
        [add_field_migration, update_test_migration],
    )
    assert "test" in ckpt
    assert ckpt["test"] == "nok"


def test_execute_missed_migrations():
    ckpt, _ = migrate_ckpt(
        {},
        [blank_migration, add_field_migration],
    )
    assert len(ckpt[ckpt_migration_key]) == 2
    new_ckpt, _ = migrate_ckpt(
        ckpt, [blank_migration, blank2_migration, add_field_migration]
    )
    assert len(new_ckpt[ckpt_migration_key]) == 2
    assert blank2_migration.name not in new_ckpt[ckpt_migration_key]
