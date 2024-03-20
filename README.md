# migrate-ckpt

```python
import torch
from migrate_ckpt import CkptType, Migration, migrate_ckpt


def update_some_keys_callback(ckpt: CkptType) -> CkptType:
    """
    Define a callback that takes a checkpoints and updates it.
    """
    ckpt["some_keys"] = ckpt["some_other_keys"]
    del ckpt["some_other_keys"]
    return ckpt


# List a set of migrations. Whenever you update your model architecture,
# you should add one that updates the model starting from the previous
# state (output of the previous migration)
model_migrations = [
    Migration("Update some keys", update_some_keys_callback),
]

# Will only perform new migrations.
# done_migrations returns the list of migration objects that were executed.
ckpt, done_migrations = migrate_ckpt(
    torch.load("/path/to/some/checkpoint.ckpt"),
    model_migrations,
)

# This has no effect, the model was already migrated.
ckpt_2, _ = migrate_ckpt(ckpt, model_migrations)
```

Note: the list of migration to perform is determined by the last done migration.
Missed migration in between will never be done.
For example, if migrations to do are ["0", "1", "2"] and model has already had migration
"1", only "2" will be done, but not "0".

## Store migrations in a folder

It migth be convenient to store all your migrations in a specific folder, and execute
migrations from this folder. You can do this with `migrate_from_folder` function.

For example, create a `migrations` folder with this files (loaded in alphabetical order):
```
0_initial_migration.py
1_second_migration.py
2_this_comes_next.py
```

In each migration file, you need to define a function:
```python
from migrate_ckpt import CkptType


def handle(ckpt: CkptType) -> CkptType:
    # do stuff with ckpt
    return ckpt
```


You can then execute all migrations in the folder with:
```python
import torch

from migrate_ckpt import migrate_from_folder

ckpt, done_migrations = migrate_from_folder(
    torch.load("/path/to/some/checkpoint.ckpt"), "path/to/migration/folder"
)
```
