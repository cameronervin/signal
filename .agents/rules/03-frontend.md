# Frontend Rules

Signal uses Next.js App Router and TypeScript.

## Structure

```text
frontend/src/app               routes and layouts
frontend/src/components/ui     reusable primitives
frontend/src/components/layout shell and navigation
frontend/src/components/features route-level feature components
frontend/src/lib/api           API client and endpoint modules
frontend/src/lib/fixtures      typed demo data
frontend/src/lib/store         UI-only Zustand state
frontend/src/types             shared contracts
```

## Do

- Server Components by default.
- Add `"use client"` only for interactivity.
- Use TanStack Query for server state.
- Use Zustand only for UI state.
- Use lucide-react icons when available.
- Keep accessible names on icon buttons.

## Do Not

- Store backend data in Zustand.
- Fetch in `useEffect` when a server component or query hook fits.
- Use `any`.
- Hardcode repeated colors outside token files.
- Add marketing landing-page sections. The first screen is the product.
