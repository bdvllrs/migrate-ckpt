from migrate_ckpt.migrate import CkptType


def handle(ckpt: CkptType) -> CkptType:
    ckpt["first_migration"] = ckpt["first_migration"] + " long ago!"
    ckpt["second_migration"] = "done"
    return ckpt
