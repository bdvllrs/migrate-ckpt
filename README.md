# migrate-ckpt

```python
import torch
from migrate_ckpt import Migration, migrate_ckpt


def update_some_keys_callback(ckpt):
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
