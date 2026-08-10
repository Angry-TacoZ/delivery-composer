# Today's deterministic demo

## Product direction

- **Visual thesis:** a restrained, graphite operations tool aligned with C86's editorial tone.
- **Content plan:** identify the brief, define requirements, execute a recommendation, assure the evidence, and learn from the human decision.
- **Interaction thesis:** the IDEAL stage strip reflects state; evidence reveals scored runners-up in place; current-versus-challenger comparisons open in a focused overlay; overrides and review actions provide immediate feedback.

## What runs today

The meeting build uses `DEMO_MODE=true`. FastAPI serves three synthetic brief scenarios, evaluates a fifteen-profile fictional roster, applies deterministic requirement rules, ranks three exact-role options for every requested role, produces evidence-bound explanations, and retains the review and any human overrides for the API session.

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
Three-candidate ranking, evidence, and visible exceptions
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
3. Open Theo's evidence to reveal Priya and Marcus as scored runners-up, then select Priya's Compare control.
4. Use the RPG-style current-versus-challenger overlay to audit `Theo: 58 + 8 + 0 = 66` against `Priya: 58 + 16 + 0 = 74`. The delta names Priya's extra required-capability match immediately. Then show that Theo is still recommended because clearance and availability are unscored hard gates; select Priya with the visible exception and point out that the failed constraints remain red instead of being rewritten as a pass.
5. Add a short review note and approve. The Learn state confirms that one human override was stored for the API session.
6. Restore the sample or select another brief to show that the override clears and the evaluation changes with the input.
7. Open the repository architecture and explain the explicit adapter switch to PostgreSQL, pgvector, and Gemini.

Explain that a greenlit version can expose the existing bounded PDF adapter through the same brief contract. Do not paste real client, candidate, or employee information into the meeting build.
