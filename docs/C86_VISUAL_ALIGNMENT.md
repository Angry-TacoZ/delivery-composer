# C86 visual alignment

## Purpose

Realign Delivery Composer with the visual language of C86's public website before the meeting demo. The working MVP currently communicates the right product idea, but its acid-green, monospaced editorial treatment is too close to JamesAI rather than the intended C86 reference.

This document is the acceptance-criteria commit used to open the draft PR before implementation begins.

## Source direction

The selected source is the C86 cybersecurity page supplied for the project. Its defining characteristics are:

- matte charcoal and graphite surfaces rather than pure black;
- thin, low-contrast trajectory and wireframe linework;
- a restrained spectral wash using navy, cyan, teal, muted rose, and violet;
- large editorial serif display copy paired with calm neutral sans-serif body copy;
- generous spacing, few borders, and minimal interface chrome;
- no lime-green accent system, pill-heavy controls, or generic dashboard-card mosaic.

The MVP may be tailored for a conversation with C86, but it must not imply that it is an official C86 product or reproduce a proprietary logo lockup.

## Implementation scope

- Preserve the existing client brief, composition, evidence expansion, and human-review workflow.
- Replace the current JamesAI-like visual tokens and brand mark.
- Introduce a real background image asset derived from the selected C86 art direction; do not recreate it as CSS gradient or div art.
- Rebalance the first viewport around a C86-like editorial introduction and a clear application workspace.
- Keep the interface responsive and keyboard-usable.
- Update repository-facing documentation, screenshots, and CI so the private GitHub repository is credible to show during the meeting.

## Acceptance criteria

- [x] A side-by-side design QA compares the supplied C86 reference with the same-size application capture.
- [x] No actionable P0, P1, or P2 design-QA findings remain.
- [x] No neon/lime accent remains in the application.
- [x] The linework/spectral visual is a checked-in raster asset with no embedded source-site text or logo.
- [x] Compose, evidence expansion, and approve/revise interactions still work.
- [x] Desktop and mobile layouts have no clipped primary controls or unintended horizontal overflow.
- [x] Browser console shows no application errors during the primary workflow.
- [x] Ruff, API tests, frontend production build, canonical verification, and the predeploy secret scan pass.
- [x] README accurately separates implemented behavior, deterministic preview behavior, and deployment work still requiring secrets/billing.
- [x] No database credential, Gemini key, paid API call, or real client/candidate data is introduced.

## Out of scope

- Changing the FastAPI/PostgreSQL/Gemini architecture.
- Loading real C86, client, candidate, or employee data.
- Claiming production readiness, C86 ownership, endorsement, or official branding.
- Deploying before billing, server-side secrets, and live database/model verification are complete.
