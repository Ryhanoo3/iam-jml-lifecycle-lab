"""Simple Joiner workflow for the IAM JML lifecycle lab."""

import json
from datetime import date, datetime
from pathlib import Path


# Build file paths from the project folder so the script works from any directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
EMPLOYEES_FILE = PROJECT_ROOT / "data" / "employees.json"
ROLES_FILE = PROJECT_ROOT / "data" / "roles.json"
IDENTITY_STATE_FILE = PROJECT_ROOT / "data" / "identity_state.json"
AUDIT_LOG_FILE = PROJECT_ROOT / "logs" / "audit.log"


def run_joiner() -> None:
    """Provision the first demo employee, Alice (E001)."""

    # Read the two input files that describe employees and role access.
    with EMPLOYEES_FILE.open(encoding="utf-8") as file:
        employees = json.load(file)

    with ROLES_FILE.open(encoding="utf-8") as file:
        roles = json.load(file)

    # This first MVP intentionally handles only Alice.
    employee = next(
        employee for employee in employees if employee["employee_id"] == "E001"
    )

    # Check that the employee is eligible to be provisioned today.
    if employee["status"].lower() != "active":
        raise ValueError("Alice is not active and cannot be provisioned.")

    start_date = date.fromisoformat(employee["start_date"])
    if start_date > date.today():
        raise ValueError("Alice's start date is in the future.")

    # Use Alice's role to find the applications and entitlement she should receive.
    access = roles[employee["role"]]

    # Create a small, readable identity record for the demo.
    identity_entry = {
        "employee_id": employee["employee_id"],
        "name": f"{employee['first_name']} {employee['last_name']}",
        "role": employee["role"],
        "identity_status": "active",
        "accounts": ["Microsoft 365", "Finance System"],
        "entitlements": ["Finance Reports - Read"],
    }

    # Ensure the state file exists and contains a JSON array before saving the update.
    IDENTITY_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    if IDENTITY_STATE_FILE.exists():
        with IDENTITY_STATE_FILE.open(encoding="utf-8") as file:
            identity_state = json.load(file)
    else:
        identity_state = []

    identity_state.append(identity_entry)
    with IDENTITY_STATE_FILE.open("w", encoding="utf-8") as file:
        json.dump(identity_state, file, indent=4)
        file.write("\n")

    # Keep a simple human-readable audit trail of the provisioning event.
    AUDIT_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().isoformat(timespec="seconds")
    audit_entry = (
        f"{timestamp} - JOINER - Provisioned {identity_entry['name']} "
        f"({employee['employee_id']}) with role {employee['role']}; "
        f"accounts: {', '.join(identity_entry['accounts'])}; "
        f"entitlement: {identity_entry['entitlements'][0]}\n"
    )
    with AUDIT_LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(audit_entry)

    print(f"Provisioned {identity_entry['name']} ({employee['employee_id']})")
    print(f"Role: {employee['role']}")
    print(f"Accounts: {', '.join(identity_entry['accounts'])}")
    print(f"Entitlement: {identity_entry['entitlements'][0]}")
    print(f"Access found in role file: {', '.join(access)}")
    print(f"Identity state written to {IDENTITY_STATE_FILE}")
    print(f"Audit entry appended to {AUDIT_LOG_FILE}")


if __name__ == "__main__":
    run_joiner()
