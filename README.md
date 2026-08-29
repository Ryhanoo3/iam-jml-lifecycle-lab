# IAM JML Lifecycle Lab

A small Python lab for demonstrating Joiner–Mover–Leaver (JML) identity and access management workflows.

## Project status

Workspace scaffold only. IAM functionality will be implemented in a later step.

## Planned capabilities

- Create identities from employee records
- Assign access based on role and birthright access rules
- Process joiner, mover, and leaver events
- Record resulting identity and entitlement state
- Produce an auditable event log

## Layout

```text
src/         Application code
data/        Sample input data and fixtures
logs/        Generated audit logs (kept out of version control)
screenshots/ Evidence captured during demonstrations
tests/       Automated tests
```

## Local setup

Create and activate a virtual environment, then install the development dependency:

```text
python -m venv .venv
python -m pip install -r requirements.txt
```

The implementation and test commands will be documented here as the lab is built.
