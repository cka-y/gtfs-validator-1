import pandas as pd
import argparse
import jsondiff
import json
from zipfile import ZipFile
import numpy as np
from utils.utils import get_migration_file


def read_rule_file(filename):
    with ZipFile(filename) as directory:
        with directory.open("rules.json") as f:
            rules = json.load(f)
    return {key: rules[key]["severityLevel"] for key in rules}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Automatic generation of NOTICE_MIGRATION.md")
    parser.add_argument('-r', '--release', help="Release Version", required=True)
    args = parser.parse_args()
    version = args.release.upper()
    output = f"**Automated Update of NOTICE_MIGRATION.md for release {version}**\n"

    migration_table: pd.DataFrame = get_migration_file()
    migration_table.fillna('', inplace=True)

    previous_version = sorted(list(migration_table.columns))[-1]
    migration_table.insert(0, version, migration_table[previous_version])

    # Read rules.json
    rules_1 = read_rule_file(f"rules-{version.lower()}")
    rules_2 = read_rule_file(f"rules-{previous_version.lower()}")

    # Added Notices
    diff = jsondiff.diff(rules_1, rules_2)
    new_notices = []
    try:
        new_notices = diff[jsondiff.delete]
        i = len(migration_table.index)
        for new_notice in new_notices:
            migration_table.loc[i + 1] = [f"{rules_1[new_notice]}-{new_notice}"] \
                                         + ['' for _ in range(len(migration_table.columns) - 1)]
            i += 1
        output += "*Notices added :* " + ", ".join(new_notices) + "\n"
    except KeyError:
        output += "*No added notices. *\n"

    # Deleted notices
    diff = jsondiff.diff(rules_2, rules_1)
    try:
        deleted_notices = diff[jsondiff.delete]
        for deleted_notice in deleted_notices:
            migration_table.loc[migration_table[migration_table[version].str.endswith(deleted_notice)].index, version] = ''
        output += "*Notices deleted :* " + ", ".join(deleted_notices) + "\n"
    except KeyError:
        output += "*No deleted notices. *\n"

    # Change in severity
    output += "*Notices change in severity level :* \n"
    for notice, severity in diff.items():
        if notice in new_notices or notice == jsondiff.delete:
            continue
        migration_table.loc[migration_table[migration_table[version].str.endswith(notice)].index, version] = \
            f"{severity}-{notice}"
        output += f"- {notice} changed from {rules_2[notice]} to {severity} \n"
    if not len(diff):
        output += "None"

    migration_table.replace('-', ' - ', regex=True, inplace=True)
    migration_table.replace('', np.nan, regex=True, inplace=True)

    # Update NOTICE_MIGRATION.md
    notice_migration_file = "docs/NOTICE_MIGRATION.md"
    with open(notice_migration_file, 'r') as f:
        file_content = f.read()

    new_file_content = "\n".join([line for line in file_content.split('\n') if not line.startswith('|')]) \
                       + "\n" + migration_table\
                           .sort_values(by=[version, previous_version], na_position='last')\
                           .fillna('')\
                           .to_markdown(index=False)

    with open(notice_migration_file, 'w') as f:
        f.write(new_file_content)
    print(output)