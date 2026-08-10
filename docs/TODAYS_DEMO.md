# Today's deterministic demo

## Product direction

- **Visual thesis:** a restrained, graphite operations tool aligned with C86's editorial tone.
- **Content plan:** identify the brief, define requirements, execute a recommendation, assure the evidence, and learn from the human decision.
- **Interaction thesis:** the IDEAL stage strip reflects state; evidence expands in place; PDF and review actions provide immediate feedback.

## What runs today

The meeting build uses `DEMO_MODE=true`. FastAPI serves three synthetic brief scenarios, applies deterministic requirement rules, filters synthetic consultants by hard constraints, ranks the remaining profiles, produces evidence-bound explanations, and retains the review for the API session.

This is real application behavior over synthetic data. It does not call Gemini, query PostgreSQL, or claim persistent learning.

```text
Synthetic brief library or editable text
              |
              v
Typed FastAPI brief contract and validation
              |
              v
Deterministic requirements and hard constraints
              |
              v
Synthetic profile ranking and evidence
              |
              v
Human approval or revision (API session)
```

## Greenlit backend path

The service boundary and response contracts are shared with the planned live implementation. A greenlit version can set `DEMO_MODE=false` and supply both server-side secrets to switch the adapters together:

```text
Gemini structured extraction and embeddings
              |
              v
PostgreSQL constraints and pgvector retrieval
              |
              v
Evidence-grounded Gemini explanations
              |
              v
PostgreSQL run and review persistence
```

Live mode fails at startup unless both `DATABASE_URL` and `GEMINI_API_KEY` are configured. Demo mode ignores configured live credentials, preventing an accidental database connection or paid model call during the meeting.

## Fifteen-minute walkthrough

1. Open the demo brief library, choose the critical-infrastructure case, and point out its synthetic reference and sector.
2. Compose the team and explain that clearance and availability are gates, not model suggestions.
3. Expand one consultant to show the profile evidence behind the score.
4. Approve or request a revision to complete Assure and Learn.
5. Reopen the library, choose the financial-services or media case, and show that requirements, roles, and team order change.
6. Open the repository architecture and explain the explicit adapter switch to PostgreSQL, pgvector, and Gemini.

Explain that a greenlit version can expose the existing bounded PDF adapter through the same brief contract. Do not paste real client, candidate, or employee information into the meeting build.
