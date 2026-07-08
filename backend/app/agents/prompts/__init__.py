"""Prompt templates and prompt-facing instructions."""

from app.agents.prompts.digital_worker import (
    DIGITAL_WORKER_SYSTEM_PROMPT,
    digital_worker_tool_prompt,
)
from app.agents.prompts.outreach import OUTREACH_DRAFT_INSTRUCTIONS

__all__ = [
    "DIGITAL_WORKER_SYSTEM_PROMPT",
    "OUTREACH_DRAFT_INSTRUCTIONS",
    "digital_worker_tool_prompt",
]
