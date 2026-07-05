# Context Engineering

Use this skill when editing prompts, graph state, or context packs.

## Principles

- Keep core prompts short and explicit.
- Put fetched data in structured fields, not prose blobs.
- Separate deterministic facts from model-generated conclusions.
- Include source ids for every fact used in outreach.
- Add stop criteria and bounded retry instructions.
- Include negative examples for gate-failed and unsupported leads.

## Signal Prompt Requirements

Prompts must tell the model:

- Do not invent company news, property details, or market stats.
- Use only supplied facts and cited source records.
- If gates fail, return flags and no draft.
- Keep output useful for SDR review, not automatic sending.
