import pandas as pd
import argparse
from utils.utils import get_migration_file

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Automatic generation of NOTICE_MIGRATION.md")
    parser.add_argument('-r', '--release', help="Release Version", required=True)
    args = parser.parse_args()
    version = args.release.upper()

    print(f"Release Version = {version}")
    migration_table: pd.DataFrame = get_migration_file()

    previous_version = sorted(list(migration_table.columns))[-1]
    migration_table.insert(0, version, migration_table[previous_version])    # For testing adding a line to the table

    notice_migration_file = "docs/NOTICE_MIGRATION.md"
    with open(notice_migration_file, 'r') as f:
        file_content = f.read()

    new_file_content = "\n".join([line for line in file_content.split('\n') if not line.startswith('|')]) \
                       + "\n" + migration_table.fillna('').to_markdown(index=False)

    with open(notice_migration_file, 'w') as f:
        f.write(new_file_content)
    print("Done.")
