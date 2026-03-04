import json
import sys
from pathlib import Path

def print_changes(changes_file):
    with open(changes_file, "r") as f:
        changes = json.load(f)

    account = changes.get("account_id", "unknown")
    version = changes.get("version_change", "v1 -> v2")

    print(f"\nAccount: {account}")
    print(f"Version: {version}")
    print("\nChanges Detected:\n")

    for field, diff in changes.get("fields_changed", {}).items():
        old = diff.get("old")
        new = diff.get("new")

        print(f"{field}")
        print(f"   old: {old}")
        print(f"   new: {new}\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python show_changes.py <changes.json>")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    print_changes(file_path)