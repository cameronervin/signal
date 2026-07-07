# Frontend Rules

Signal uses Next.js App Router, React 19, TypeScript, Tailwind v4, Jest, Testing Library, and pnpm.

## Structure

```text
frontend/src/app/                 App Router routes
frontend/src/components/layout/   Shared shell
frontend/src/components/ui/       Signal primitives
frontend/src/lib/api/             Backend API client
frontend/src/lib/fixtures/        Typed demo fallback data
frontend/src/lib/constants/       Routes and constants
frontend/src/types/               Shared frontend contracts
```

## Do

- Use Server Components by default; add `'use client'` only for interactivity, browser APIs, or hooks.
- Keep route files as default exports and reusable components as named exports.
- Type props with `interface Props`.
- Use `cn()` for conditional classes.
- Use existing primitives before creating new ones.
- Keep fixtures typed and aligned with backend DTOs.
- Preserve explicit loading, error, empty, gate-failed, and awaiting-review states.

## Avoid

- `any`.
- Fetching in component bodies without an established pattern.
- Storing trusted score, tier, gate, or send state from client input.
- Adding client state libraries unless a plan explicitly adopts them.
- Copying prototype HTML directly into production code.

## Verification

```bash
pnpm --dir frontend test
pnpm --dir frontend lint
pnpm --dir frontend typecheck
```
