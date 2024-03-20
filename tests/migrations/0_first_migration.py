from migrate_ckpt.migrate import CkptType


def handle(ckpt: CkptType) -> CkptType:
    ckpt["first_migration"] = "done"
    return ckpt
