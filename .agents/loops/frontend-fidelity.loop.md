# Frontend Fidelity Loop

Use this for design-system and screen implementation.

## Context Pack

Read:

- `backstage/design/README.md`
- `.agents/style/design-tokens.md`
- `.agents/style/ui-patterns.md`
- Relevant frontend route/component files.

## Loop

1. Identify the exact screen or component.
2. Implement reusable primitives first.
3. Wire typed fixture data or API hooks.
4. Verify desktop and narrow layouts.
5. Check text fit, accessible names, hover/focus states, and gate-failed states.
6. Add component tests when behavior is more than static rendering.

## Convergence

Stop when the implemented surface matches the design intent and no text or UI
controls overlap at expected breakpoints.
