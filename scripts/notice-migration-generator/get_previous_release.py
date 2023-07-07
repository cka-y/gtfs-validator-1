import os
from utils.utils import get_migration_file

if __name__ == '__main__':
    migration_table = get_migration_file()
    previous_version = sorted(list(migration_table.columns))[-1].lower()
    os.environ["PREVIOUS_VERSION"] = previous_version
    print(previous_version)
