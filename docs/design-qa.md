# Design QA: C86 visual alignment

## Compared sources

- Reference: user-supplied C86 cybersecurity page capture, 2048 × 1200 pixels.
- Implementation: `docs/screenshots/delivery-composer-hero.png`, 2048 × 1200 pixels.
- Browser state: first viewport, populated sample brief, before composition.
- Rendering density: desktop browser at 1× CSS scale.

The reference and implementation were opened together at their native dimensions for the comparison pass.

## Full-frame comparison

The implementation matches the source direction at the system level: matte charcoal surfaces, thin grey trajectory arcs, restrained white editorial type, serif emphasis, generous negative space, and a cyan/rose/violet spectral field at the section boundary. The application remains clearly labeled as a concept rather than reproducing the C86 logo or presenting itself as an official product.

The composition intentionally adapts the source from a marketing section into an operations tool. The first viewport establishes the shared visual language; the application workspace below uses straight borders, no card mosaic, and no pill-heavy controls.

## Focused checks

- **Line field:** the checked-in raster has no source-site logo or text. Its hero layer changes transform over time, producing a visible slow trajectory drift; `prefers-reduced-motion` reduces all animation to a still frame.
- **Typography:** display scale, serif emphasis, neutral body text, and restrained uppercase labels follow the supplied hierarchy without copying source text.
- **Color:** no lime or neon-green application token remains. Cyan is used only for process and verification cues.
- **Primary workflow:** client brief, composition, evidence expansion, approve action, and recorded-review confirmation are functional.
- **Desktop:** 2048 × 1200 viewport showed no clipped primary action or console warning/error.
- **Mobile:** 390 × 844 viewport showed no unintended horizontal overflow; the compose and approve flows completed without a console warning/error.

## Iteration history

1. Removed the previous lime, monospaced personal-brand treatment and homemade SVG brand mark.
2. Rebuilt the first viewport around the supplied C86 structure and generated a clean text-free raster line field.
3. Added slow transform-based trajectory motion and a reduced-motion fallback.
4. Rebalanced the application workspace, expanded evidence state, and human-review section against the same straight-line visual system.
5. Rechecked the source and implementation together at the same 2048 × 1200 viewport.

## Findings

- P0: none.
- P1: none.
- P2: none.
- P3: the concept uses system Georgia rather than a licensed C86 display face; this is an intentional portable fallback for the private MVP.

## Final result

passed
