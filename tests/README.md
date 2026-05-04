# Tests

Automated tests — populated during project implementation.

## Scope
Tests are written for critical paths only:
- Authentication flows (login, token validation, logout)
- Payment flows (if applicable)
- Data mutations (create, update, delete on core entities)
- API integrations (external service calls)

## Expected Structure
```
tests/
├── unit/           — isolated function/module tests
├── integration/    — API endpoint tests (real database)
└── e2e/            — end-to-end user journey tests (if applicable)
```

## Stack
Defined in `design/stack_selection.md` during planning.

## Running Tests
Project-specific commands added during setup.
