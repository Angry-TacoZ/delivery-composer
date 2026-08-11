# PDF brief QA

## Final artifacts

- `output/pdf/critical-infrastructure-cyber-resilience.pdf`
- `output/pdf/financial-services-ai-governance.pdf`
- `output/pdf/media-broadcast-platform-recovery.pdf`

Each file is one A4 page, contains synthetic demonstration data only, and includes a visible non-client disclaimer.

## Rendering review

All three PDFs were rendered through Poppler at 144 DPI to 1191 x 1684 PNGs and inspected at original resolution. Typography, line wrapping, margins, metadata boxes, section hierarchy, accent line, footer, and page numbering are aligned and legible. No clipped text, overlap, broken glyph, unreadable contrast, or unintended additional page was found.

## Extraction and evaluation evidence

| PDF | Pages | Extracted characters | Requirements title | Ordered team |
|---|---:|---:|---|---|
| Critical infrastructure | 1 | 1,054 | Critical infrastructure resilience delivery team | Theo Morgan, Maya Patel, Amina Okafor |
| Financial services | 1 | 985 | Financial services AI governance delivery team | Theo Morgan, Amina Okafor, Elena Rossi |
| Media and broadcast | 1 | 997 | Media and broadcast platform recovery team | Theo Morgan, Jon Bell, Elena Rossi |

The media comparison exposed a false-positive `ai` substring match inside unrelated prose. The deterministic trigger was tightened to explicit AI phrases and the regression is covered by an automated assertion.

## Browser review

- Desktop: actual file chooser upload, inline filename/page/character provenance, visible editable extraction, composition, evidence expansion, distinct requirement output, and error recovery passed at 2048 x 1200.
- Mobile: source row and upload control stack to 335 pixels inside a 390 x 844 viewport; document-level scroll width remained 375 pixels.
- Invalid file: a `.pdf` with no PDF signature returned a recoverable validation message and no stale evaluation remained visible.
- Console: no warnings or errors during the primary PDF workflow.
- The earlier upload-interface screenshot is intentionally excluded because file selection is not exposed in the current public portfolio workflow.

## Final result

passed
