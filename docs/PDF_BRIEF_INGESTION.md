# PDF client brief ingestion

> **Meeting-mode update:** the current UI intentionally presents the three synthetic cases through an inline demo brief library. The bounded extraction endpoint and generated PDF fixtures remain as a tested future integration boundary; actual file selection is not exposed during today's demo.

## Purpose

Preserve a bounded route for a future delivery leader to upload a concise client brief as a PDF, inspect the extracted text, and run it through the same transparent evaluator used by manual entry. For today's meeting, expose the distinct synthetic briefs through the faster and more explicit demo library.

This planning document is intentionally committed before runtime implementation and is the basis for stacked draft PR #3.

## Pull request relationship

PR #3 is based on `codex/ideal-methodology-alignment` while PR #2 is under review. It should target that branch until PR #2 merges, then be rebased or retargeted to `main` without mixing the two review scopes.

## Trust boundaries

- The browser selects one untrusted local file and sends it to FastAPI as multipart form data.
- FastAPI owns file validation and text extraction. PDF parsing does not occur in browser-delivered code.
- Extracted text is returned to the editable brief field and evaluated through the existing bounded `BriefInput` contract.
- Uploaded bytes and extracted text are not persisted by the extraction endpoint.
- Aiven and Gemini secrets remain server-only and are not involved in PDF parsing.

## Extraction contract

- Accept one `.pdf` file with `application/pdf` content type.
- Require a `%PDF-` file signature instead of trusting the filename alone.
- Read at most 2 MiB plus one sentinel byte; reject larger files.
- Accept at most five pages.
- Reject encrypted, malformed, image-only, empty, too-short, and overlong extracted briefs with useful generic errors.
- Normalize whitespace and require 40-1,600 extracted characters so PDF and manual entry share the same evaluator boundary.
- Return only a bounded display filename, page count, character count, and extracted text.
- Do not provide OCR in this MVP; document that scanned PDFs must be converted to searchable text first.

## Demo scenarios

Create polished, one-page, synthetic PDFs under `output/pdf/`:

1. Critical infrastructure cyber resilience - SC clearance, zero trust, cloud, data governance, and security operations.
2. Financial services AI governance - baseline clearance, governed data, AI engineering, and regulatory delivery.
3. Media and broadcast platform recovery - baseline clearance, platform engineering, cloud automation, incident response, and a later start date.

The deterministic preview must derive distinct titles, skills, sectors, roles, start dates, summaries, and team compositions from these briefs. This keeps the offline meeting path honest without making a paid model call.

## Product design

**Visual thesis:** extend the existing graphite editorial workbench with a restrained document-ingestion control that looks operational, not like a generic upload card.

**Content plan:** source selector and status sit directly above the editable brief; extracted text remains fully visible; existing composition and evidence areas remain unchanged.

**Interaction thesis:** filename and extraction state update inline, the populated text receives normal focus, and existing result reveal/stage transitions provide the primary motion. No new decorative animation is needed.

## Acceptance criteria

- [x] The retained API accepts a bounded searchable PDF and returns extracted text for review before evaluation.
- [x] Manual edits, restore-sample, demo-library selection, and the retained PDF adapter all use the same bounded brief contract.
- [x] The server enforces MIME, extension, signature, byte-size, page-count, encryption, text-presence, and text-length boundaries.
- [x] Upload errors are specific enough to recover from but expose no stack traces, file paths, or parser internals.
- [x] Uploaded bytes are not persisted and no PDF content is logged.
- [x] The UI identifies the source filename, page count, and extracted character count without pill-heavy styling.
- [x] Keyboard, label, loading, success, error, and mobile states remain accessible.
- [x] Three final synthetic PDFs are generated, text-extracted, rendered to PNG, and visually inspected.
- [x] Each synthetic brief produces different structured requirements and a different ordered team in deterministic preview mode.
- [x] Dynamic summaries describe the actual requested roles rather than the original hard-coded cyber scenario.
- [x] Tests cover a valid PDF and malformed, wrong-type, oversized, encrypted, image-only, too-many-page, and overlong cases.
- [x] Existing manual composition, IDEAL stages, evidence expansion, and review persistence continue to work.
- [x] README and handoff describe the PDF boundary, sample artifacts, and stacked-PR dependency.
- [x] Canonical verification, dependency audit, predeploy secret scan, browser checks, and GitHub Actions pass.

## Out of scope

- OCR for scanned or photographed documents.
- Word, PowerPoint, image, or email ingestion.
- Persisting original PDFs or extracted text outside the existing configured composition path.
- Antivirus or content-disarm processing for production document storage.
- Real client data, client names, employee data, or confidential engagement material.
- Connecting Aiven, Gemini, Firebase Hosting, or Cloud Run credentials in this PR.
