# Style Guide

Visual design system. Read during planning and first implementation session, then rely on design_summary.md.

## Design Language

**Baseline**: Glassmorphism — frosted glass panels, subtle blur, layered depth.
- Light mode: white/light-gray backgrounds, dark text, soft shadows
- Dark mode: deep navy/charcoal backgrounds, light text, glow accents
- Toggle: persistent user preference, stored in localStorage

## Typography

| Role | Size | Weight | Notes |
|------|------|--------|-------|
| Heading 1 | 2rem | 700 | Page titles |
| Heading 2 | 1.5rem | 600 | Section titles |
| Body | 1rem | 400 | Default text |
| Small | 0.875rem | 400 | Labels, captions |
| Mono | 0.875rem | 400 | Code, keys |

(Adjust per project — populated during planning)

## Colors

| Token | Light | Dark | Use |
|-------|-------|------|-----|
| surface | #ffffff/90% | #1a1a2e/80% | Card backgrounds |
| border | rgba(255,255,255,0.2) | rgba(255,255,255,0.1) | Panel borders |
| accent | [project color] | [project color] | CTAs, highlights |
| text-primary | #1a1a2e | #f0f0f0 | |
| text-secondary | #6b7280 | #9ca3af | |
| danger | #ef4444 | #f87171 | Errors, destructive |
| success | #10b981 | #34d399 | Confirmations |

## Spacing

Base unit: 4px. Scale: 4, 8, 12, 16, 24, 32, 48, 64.

## Responsive Breakpoints

| Name | Min-width | Layout |
|------|-----------|--------|
| mobile | 0 | Single column, bottom nav |
| tablet | 768px | Sidebar collapsed |
| desktop | 1024px | Sidebar expanded |

## Component Patterns

- **Cards**: Frosted glass, rounded-xl, subtle shadow
- **Buttons**: Primary (accent fill), Secondary (outline), Danger (red)
- **Forms**: Floating labels or clear labels above fields
- **Tables**: Zebra rows, sticky header, pagination footer
- **Pipeline nodes**: Colored by state (gray/blue/green/red/yellow)
