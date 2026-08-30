"""Simple Leaver workflow for the IAM JML lifecycle lab."""

import json
from datetime import datetime
from pathlib import Path


# Build file paths from the project folder so the script works from any directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
IDENTITY_STATE_FILE = PROJECT_ROOT / "data" / "identity_state.json"
AUDIT_LOG_FILE = PROJECT_ROOT / "logs" / "audit.log"


def display_access(access_items: list[str]) -> str:
    """Make an access list readable in the terminal and audit log."""
    return ", ".join(access_items) if access_items else "none"


def run_leaver() -> None:
    """Deprovision Alice (E001) while preserving her identity record."""

    # Read the current identity state before changing any access.
    with IDENTITY_STATE_FILE.open(encoding="utf-8") as file:
        identity_state = json.load(file)

    alice = next(
        entry for entry in identity_state if entry["employee_id"] == "E001"
    )

    # If Alice is already fully deprovisioned, do not create another audit event.
    if (
        alice["identity_status"] == "inactive"
        and not alice["accounts"]
        and not alice["entitlements"]
    ):
        print("Alice Smith (E001) is already inactive with no access.")
        print("No changes made and no duplicate audit event created.")
        return

    # Save the old role and access for the audit record before removing anything.
    previous_role = alice["role"]
    removed_accounts = list(alice["accounts"])
    removed_entitlements = list(alice["entitlements"])

    # Deactivate the identity but preserve the record for historical auditing.
    alice["identity_status"] = "inactive"
    alice["accounts"] = []
    alice["entitlements"] = []

    with IDENTITY_STATE_FILE.open("w", encoding="utf-8") as file:
        json.dump(identity_state, file, indent=4)
        file.write("\n")

    # Record exactly what was revoked and leave the identity history intact.
    AUDIT_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().isoformat(timespec="seconds")
    audit_entry = (
        f"{timestamp} - LEAVER - Employee E001 ({alice['name']}) deprovisioned; "
        f"previous role: {previous_role}; "
        f"accounts removed: {display_access(removed_accounts)}; "
        f"entitlements removed: {display_access(removed_entitlements)}; "
        f"final identity status: inactive\n"
    )
    with AUDIT_LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(audit_entry)

    print(f"Deprovisioned {alice['name']} (E001) from role {previous_role}")
    print(f"Accounts removed: {display_access(removed_accounts)}")
    print(f"Entitlements removed: {display_access(removed_entitlements)}")
    print("Final identity status: inactive")
    print(f"Identity state written to {IDENTITY_STATE_FILE}")
    print(f"Audit entry appended to {AUDIT_LOG_FILE}")


if __name__ == "__main__":
    run_leaver()
