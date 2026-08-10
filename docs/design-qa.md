# Design QA: C86 visual alignment and IDEAL workflow

## Compared sources

- Reference: user-supplied C86 cybersecurity page capture, 2048 × 1200 pixels.
- Implementation: `docs/screenshots/delivery-composer-hero.png`, 2048 × 1200 pixels.
- IDEAL implementation state: `docs/screenshots/delivery-composer-ideal-initial.png`, 2048 × 1200 pixels.
- Browser state: first viewport, populated sample brief, before composition.
- Rendering density: desktop browser at 1× CSS scale.

The reference and implementation were opened together at their native dimensions for the comparison pass.

## Full-frame comparison

The implementation matches the source direction at the system level: matte charcoal surfaces, thin grey trajectory arcs, restrained white editorial type, serif emphasis, generous negative space, and a cyan/rose/violet spectral field at the section boundary. The application remains clearly labeled as a concept rather than reproducing the C86 logo or presenting itself as an official product.

The composition intentionally adapts the source from a marketing section into an operations tool. The first viewport establishes the shared visual language; the application workspace below uses straight borders, no card mosaic, and no pill-heavy controls.

The methodology screenshot was treated as workflow content, not as a new visual target. The approved graphite editorial system, line animation, spectral field, typography, spacing, and square controls remain unchanged while the process strip now represents Identify, Define, Execute, Assure, and Learn.

## Focused checks

- **Line field:** the checked-in raster has no source-site logo or text. Its hero layer changes transform over time, producing a visible slow trajectory drift; `prefers-reduced-motion` reduces all animation to a still frame.
- **Typography:** display scale, serif emphasis, neutral body text, and restrained uppercase labels follow the supplied hierarchy without copying source text.
- **Color:** no lime or neon-green application token remains. Cyan is used only for process and verification cues.
- **Primary workflow:** client brief, composition, evidence expansion, approve/revision actions, bounded review notes, and persistence-specific confirmation are functional.
- **IDEAL state:** Identify starts active; composition completes Identify, Define, and Execute and makes Assure active; a stored human review completes Assure and Learn.
- **Desktop:** 2048 × 1200 viewport showed no clipped primary action or console warning/error.
- **Mobile:** 390 × 844 viewport showed no document-level horizontal overflow; the five-stage strip scrolls within its own boundary and the compose, notes, and approve flows completed.

## Iteration history

1. Removed the previous lime, monospaced personal-brand treatment and homemade SVG brand mark.
2. Rebuilt the first viewport around the supplied C86 structure and generated a clean text-free raster line field.
3. Added slow transform-based trajectory motion and a reduced-motion fallback.
4. Rebalanced the application workspace, expanded evidence state, and human-review section against the same straight-line visual system.
5. Rechecked the source and implementation together at the same 2048 × 1200 viewport.
6. Preserved that visual target while introducing the five-stage IDEAL state model and real review-persistence provenance.

## Findings

- P0: none.
- P1: none.
- P2: none.
- P3: the concept uses system Georgia rather than a licensed C86 display face; this is an intentional portable fallback for the private MVP.

## Final result

passed
