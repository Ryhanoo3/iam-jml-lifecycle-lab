"""Reset generated files so the JML lifecycle demo can be run again."""

from pathlib import Path


# Build file paths from the project folder so the script works from any directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
IDENTITY_STATE_FILE = PROJECT_ROOT / "data" / "identity_state.json"
AUDIT_LOG_FILE = PROJECT_ROOT / "logs" / "audit.log"


def reset_demo() -> None:
    """Return the demo to its clean state without changing the sample data."""

    # The lifecycle starts with no provisioned identities.
    IDENTITY_STATE_FILE.write_text("[]\n", encoding="utf-8")

    # The audit log is generated output, so clear it before a fresh demonstration.
    AUDIT_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_LOG_FILE.write_text("", encoding="utf-8")

    print("Demo reset complete.")
    print("identity_state.json is empty and audit.log has been cleared.")


if __name__ == "__main__":
    reset_demo()
