"""Simple Mover workflow for the IAM JML lifecycle lab."""

import json
from datetime import datetime
from pathlib import Path


# Build file paths from the project folder so the script works from any directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ROLES_FILE = PROJECT_ROOT / "data" / "roles.json"
IDENTITY_STATE_FILE = PROJECT_ROOT / "data" / "identity_state.json"
AUDIT_LOG_FILE = PROJECT_ROOT / "logs" / "audit.log"


def display_access(access_items: list[str]) -> str:
    """Make an access list readable in the terminal and audit log."""
    return ", ".join(access_items) if access_items else "none"


def run_mover() -> None:
    """Move Alice (E001) from her current role to HR Administrator."""

    # Read the role definitions that contain the target role's access.
    with ROLES_FILE.open(encoding="utf-8") as file:
        roles = json.load(file)

    # Read Alice's current identity state.
    with IDENTITY_STATE_FILE.open(encoding="utf-8") as file:
        identity_state = json.load(file)

    alice = next(
        entry for entry in identity_state if entry["employee_id"] == "E001"
    )
    target_role = "HR Administrator"
    old_role = alice["role"]
    target_access = roles[target_role]

    # Compare each access category separately to find removed, added, and shared access.
    old_accounts = set(alice["accounts"])
    new_accounts = set(target_access["accounts"])
    old_entitlements = set(alice["entitlements"])
    new_entitlements = set(target_access["entitlements"])

    removed_accounts = sorted(old_accounts - new_accounts)
    added_accounts = sorted(new_accounts - old_accounts)
    retained_accounts = sorted(old_accounts & new_accounts)
    removed_entitlements = sorted(old_entitlements - new_entitlements)
    added_entitlements = sorted(new_entitlements - old_entitlements)
    retained_entitlements = sorted(old_entitlements & new_entitlements)

    all_removed = removed_accounts + removed_entitlements
    all_added = added_accounts + added_entitlements
    all_retained = retained_accounts + retained_entitlements

    # If Alice already matches the target role and access, there is nothing to do.
    if (
        old_role == target_role
        and alice["accounts"] == target_access["accounts"]
        and alice["entitlements"] == target_access["entitlements"]
    ):
        print("Alice Smith (E001) is already an HR Administrator with the correct access.")
        print("No changes made and no duplicate audit event created.")
        return

    # Update Alice using the target role data rather than a hardcoded final access list.
    alice["role"] = target_role
    alice["accounts"] = target_access["accounts"]
    alice["entitlements"] = target_access["entitlements"]

    with IDENTITY_STATE_FILE.open("w", encoding="utf-8") as file:
        json.dump(identity_state, file, indent=4)
        file.write("\n")

    # Record the role change and the access comparison in the audit log.
    AUDIT_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().isoformat(timespec="seconds")
    audit_entry = (
        f"{timestamp} - MOVER - Moved {alice['name']} (E001) from {old_role} "
        f"to {target_role}; removed: {display_access(all_removed)}; "
        f"added: {display_access(all_added)}; "
        f"retained: {display_access(all_retained)}\n"
    )
    with AUDIT_LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(audit_entry)

    print(f"Moved {alice['name']} (E001) from {old_role} to {target_role}")
    print(f"Access removed: {display_access(all_removed)}")
    print(f"Access added: {display_access(all_added)}")
    print(f"Access retained: {display_access(all_retained)}")
    print(f"Identity state written to {IDENTITY_STATE_FILE}")
    print(f"Audit entry appended to {AUDIT_LOG_FILE}")


if __name__ == "__main__":
    run_mover()
