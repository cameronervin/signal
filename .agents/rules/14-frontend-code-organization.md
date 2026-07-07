# Frontend Code Organization

## Structure

```text
frontend/src/app/                 App Router routes
frontend/src/components/layout/   App shell and navigation
frontend/src/components/ui/       Signal primitives
frontend/src/lib/api/             API client
frontend/src/lib/fixtures/        Typed fixture fallback data
frontend/src/lib/constants/       Routes and stable constants
frontend/src/lib/utils/           Shared utilities
frontend/src/types/               Shared contracts
```

## Rules

- Route files default export; reusable components use named exports.
- Components use `interface Props`.
- Keep files focused; split before adding unrelated behavior.
- Use `cn()` for conditional classes.
- Put repeated route names, labels, and dimensions in constants when reuse emerges.
- API functions call the API client; fixtures remain explicit fallback adapters.
- Do not add new frontend state libraries without a plan.

## Compatibility

- Keep frontend DTOs aligned with backend Pydantic responses.
- Missing or deferred backend behavior must have typed fixture fallback for demo reliability.
- Never expose controls that imply a draft/send exists for hard-gate-failed leads.
