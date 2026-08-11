# Portfolio demo guide

## What runs

The public build uses `DEMO_MODE=true`. FastAPI serves three synthetic briefs, evaluates fifteen fictional profiles, applies deterministic requirements and hard constraints, ranks three options for each requested role, and retains decisions temporarily for the API session.

It does not call Gemini, query PostgreSQL, or claim persistent learning.

```text
Synthetic brief or editable text
              |
              v
Typed FastAPI validation
              |
              v
Deterministic requirements and constraints
              |
              v
Attributable ranking and visible exceptions
              |
              v
Human approval or linked revision
```

## Suggested walkthrough

1. Choose a synthetic brief and compose its proposed team.
2. Explain that clearance and availability are gates rather than model suggestions.
3. Expand a recommendation to reveal two scored alternatives.
4. Compare candidates and audit the score arithmetic alongside unscored exceptions.
5. Select a challenger to demonstrate a visible, human-controlled override.
6. Approve the recommendation or request a revision with actionable feedback.
7. Re-evaluate and inspect the linked prior-versus-current result.
8. Show the architecture boundary between the verified deterministic demo and optional live adapters.

## Extension path

A production version can expose the existing bounded PDF adapter and enable PostgreSQL/pgvector plus Gemini through server-side configuration. Those integrations require separate live verification, persistence controls, authentication, and abuse safeguards.

Never enter real client, employee, consultant, candidate, regulated, or confidential information into the public demo.
