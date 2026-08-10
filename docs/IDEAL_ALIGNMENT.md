# C86 IDEAL methodology alignment

## Purpose

Align Delivery Composer's real product workflow with C86's IDEAL methodology without changing the approved C86-inspired visual direction or implying that this concept is an official C86 product.

This planning document is intentionally committed before runtime implementation and is the basis for the draft pull request.

## Authoritative source

C86's methodology page defines a continuous cycle:

1. **Identify the opportunity** — understand the customer environment, align stakeholders, and locate the highest-impact change.
2. **Define the path forward** — translate business objectives into strategy, architecture, and delivery plans.
3. **Execute with pace** — combine advisory insight with practical, ethical implementation and support.
4. **Assure the outcome** — use oversight, security, and validation to keep solutions resilient and programmes on track.
5. **Learn and improve** — capture lessons, refine methods, and strengthen future delivery.

Source: <https://www.c86.tech/methodology>

## Delivery Composer mapping

| IDEAL stage | Product behavior | Evidence in the MVP |
|---|---|---|
| Identify | Capture the client environment, intended outcome, stakeholders, constraints, and highest-impact needs from the brief. | Bounded client brief plus structured requirement extraction. |
| Define | Turn the opportunity into a proposed delivery shape with roles and non-negotiable requirements. | Requested roles, required skills, sectors, clearance, and delivery constraints. |
| Execute | Compose an eligible team at pace using deterministic rules or the configured PostgreSQL/pgvector path. | Ranked three-person recommendation with explicit retrieval provenance. |
| Assure | Validate clearance, availability, capability, and supporting evidence before a decision. | Hard-constraint checks, evidence expansion, rationale, and human approval boundary. |
| Learn | Capture the decision and bounded reviewer notes so the recommendation can be refined and future delivery improved. | Session-backed feedback in demo mode; PostgreSQL-backed review persistence when the live path is configured. |

## Functional gaps to close

- Replace the current four-step method strip with five stateful IDEAL stages.
- Show which stage is active or complete before composition, after composition, and after review.
- Collect optional bounded review notes for both approval and revision decisions.
- Persist demo reviews in server memory for the process lifetime rather than returning a misleading success with no storage.
- Return and display whether the review was stored in the current session or PostgreSQL.
- Keep review feedback advisory and synthetic; do not imply model retraining or autonomous organizational learning.
- Preserve the current graphite editorial layout, animated line field, responsive behavior, and reduced-motion handling.

## Acceptance criteria

- [x] The interface names and orders all five stages: Identify, Define, Execute, Assure, Learn.
- [x] Stage descriptions accurately reflect C86's published methodology and the actual product behavior.
- [x] Stage state changes are visible across initial, composing, recommendation-ready, and reviewed states.
- [x] Optional review notes are server-validated and limited to 600 characters.
- [x] Demo review submissions are stored for the API process lifetime and labeled `session` persistence.
- [x] Configured PostgreSQL review submissions remain labeled `postgres` persistence.
- [x] The UI never says a decision was recorded without identifying the persistence boundary.
- [x] Existing compose, evidence expansion, approve, and revision workflows still work.
- [x] Desktop and mobile layouts retain the approved C86 visual system without overflow or inaccessible controls.
- [x] Tests cover demo review storage and response provenance.
- [x] README and handoff explain IDEAL alignment without claiming C86 endorsement.
- [x] Canonical verification, secret scan, browser checks, and GitHub Actions pass.

## Out of scope

- Recreating the methodology screenshot or C86's circular methodology graphic.
- Using C86's logo, proprietary site assets, or claiming official C86 ownership or endorsement.
- Training or fine-tuning a model from review feedback.
- Connecting Aiven or Gemini credentials as part of this methodology-only PR.
- Deploying before the separately documented hosting and live-integration gates are complete.
