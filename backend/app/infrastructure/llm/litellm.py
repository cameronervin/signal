from __future__ import annotations

import json
from typing import Any

from langchain_core.tools import BaseTool

from app.agents.context import build_outreach_context
from app.core.config import Settings
from app.infrastructure.llm.base import DraftOutreachResult
from app.infrastructure.public_data import PublicDataClient
from app.schemas.lead import (
    DraftEmail,
    Enrichment,
    GateResult,
    LeadCreate,
    ScoreBreakdown,
    SourceFact,
)


class LiteLLMProvider:
    provider_name = "litellm"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def draft_outreach(
        self,
        *,
        lead: LeadCreate,
        gates: GateResult,
        enrichment: Enrichment,
        score: ScoreBreakdown,
        talking_points: list[str],
        instructions: str,
        tools: list[BaseTool],
        public_data_client: PublicDataClient,
    ) -> DraftOutreachResult:
        import litellm

        messages = _draft_messages(
            instructions=instructions,
            lead=lead,
            gates=gates,
            enrichment=enrichment,
            score=score,
            talking_points=talking_points,
        )
        active_tools = (
            tools
            if self.settings.agent_research_tools_enabled
            and self.settings.agent_research_max_tool_rounds > 0
            else []
        )
        tool_definitions = _tool_definitions(active_tools)
        tool_by_name = {tool.name: tool for tool in active_tools}
        tool_call_names: list[str] = []
        supplemental_sources: list[SourceFact] = []
        warnings: list[str] = []
        tool_rounds = 0

        while True:
            request_tools = (
                tool_definitions
                if tool_definitions
                and tool_rounds < self.settings.agent_research_max_tool_rounds
                else None
            )
            try:
                response = await litellm.acompletion(
                    model=_litellm_sdk_model(self.settings.llm_model),
                    api_base=self.settings.litellm_api_base,
                    api_key=self.settings.litellm_api_key,
                    messages=messages,
                    tools=request_tools,
                    tool_choice="auto" if request_tools else None,
                    parallel_tool_calls=False if request_tools else None,
                    temperature=0.2,
                )
            except Exception:
                if request_tools:
                    warnings.append("agent research tools unavailable")
                    tool_definitions = []
                    tool_by_name = {}
                    continue
                raise

            message = response.choices[0].message
            tool_calls = _message_tool_calls(message)
            if tool_calls and request_tools:
                messages.append(_assistant_tool_call_message(message))
                for tool_call in tool_calls:
                    tool_name = _tool_call_name(tool_call)
                    tool_call_names.append(tool_name)
                    content = await _invoke_tool_call(
                        tool_call=tool_call,
                        tool_by_name=tool_by_name,
                        public_data_client=public_data_client,
                    )
                    supplemental_sources.extend(_source_facts_from_tool_content(content))
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": _tool_call_id(tool_call),
                            "name": tool_name,
                            "content": content,
                        }
                    )
                tool_rounds += 1
                continue

            content = _message_content(message)
            if not content:
                return DraftOutreachResult(
                    draft=None,
                    tool_call_names=tuple(tool_call_names),
                    warnings=tuple(warnings),
                )
            return DraftOutreachResult(
                draft=DraftEmail(
                    subject=f"Improving leasing response in {lead.city}",
                    body=content,
                    sources=_dedupe_sources(
                        [*enrichment.sources, *supplemental_sources]
                    ),
                ),
                tool_call_names=tuple(tool_call_names),
                warnings=tuple(warnings),
            )


def _litellm_sdk_model(model: str) -> str:
    if "/" in model:
        return model
    return f"openai/{model}"


def _draft_messages(
    *,
    instructions: str,
    lead: LeadCreate,
    gates: GateResult,
    enrichment: Enrichment,
    score: ScoreBreakdown,
    talking_points: list[str],
) -> list[dict[str, Any]]:
    context = build_outreach_context(
        lead=lead,
        gates=gates,
        enrichment=enrichment,
        score=score,
        talking_points=talking_points,
    )
    return [
        {"role": "system", "content": instructions.strip()},
        {
            "role": "user",
            "content": (
                "Draft a concise SDR-reviewed email using only the deterministic "
                "baseline context and any returned tool source facts. Do not change "
                "score, tier, gates, or talking points.\n\n"
                f"Context: {json.dumps(context, sort_keys=True)}"
            ),
        },
    ]


def _tool_definitions(tools: list[BaseTool]) -> list[dict[str, Any]]:
    definitions: list[dict[str, Any]] = []
    for tool in tools:
        definitions.append(
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.tool_call_schema.model_json_schema(),
                },
            }
        )
    return definitions


async def _invoke_tool_call(
    *,
    tool_call: Any,
    tool_by_name: dict[str, BaseTool],
    public_data_client: PublicDataClient,
) -> str:
    tool_name = _tool_call_name(tool_call)
    tool = tool_by_name.get(tool_name)
    if tool is None:
        return _tool_unavailable(f"Tool {tool_name!r} is not available.")
    try:
        arguments = _tool_call_arguments(tool_call)
        result = await tool.ainvoke(
            {
                **arguments,
                "public_data_client": public_data_client,
            }
        )
    except Exception:  # noqa: BLE001
        return _tool_unavailable(f"Tool {tool_name!r} failed safely.")
    return str(result)


def _tool_call_arguments(tool_call: Any) -> dict[str, Any]:
    function = _obj_get(tool_call, "function", {})
    raw_arguments = _obj_get(function, "arguments", {})
    if isinstance(raw_arguments, dict):
        return raw_arguments
    try:
        parsed = json.loads(str(raw_arguments or "{}"))
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _message_tool_calls(message: Any) -> list[Any]:
    tool_calls = _obj_get(message, "tool_calls", None)
    if not tool_calls:
        return []
    return list(tool_calls)


def _message_content(message: Any) -> str | None:
    content = _obj_get(message, "content", None)
    return str(content) if content else None


def _assistant_tool_call_message(message: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "role": "assistant",
        "content": _message_content(message),
        "tool_calls": [],
    }
    for tool_call in _message_tool_calls(message):
        payload["tool_calls"].append(
            {
                "id": _tool_call_id(tool_call),
                "type": _obj_get(tool_call, "type", "function"),
                "function": {
                    "name": _tool_call_name(tool_call),
                    "arguments": _obj_get(
                        _obj_get(tool_call, "function", {}),
                        "arguments",
                        "{}",
                    ),
                },
            }
        )
    return payload


def _tool_call_id(tool_call: Any) -> str:
    value = _obj_get(tool_call, "id", None)
    return str(value) if value else f"tool_{_tool_call_name(tool_call)}"


def _tool_call_name(tool_call: Any) -> str:
    function = _obj_get(tool_call, "function", {})
    return str(_obj_get(function, "name", "unknown_tool"))


def _obj_get(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _source_facts_from_tool_content(content: str) -> list[SourceFact]:
    try:
        payload = json.loads(content)
    except json.JSONDecodeError:
        return []
    source_facts = payload.get("source_facts") if isinstance(payload, dict) else None
    if not isinstance(source_facts, list):
        return []
    facts: list[SourceFact] = []
    for source in source_facts:
        if not isinstance(source, dict):
            continue
        try:
            facts.append(SourceFact.model_validate(source))
        except ValueError:
            continue
    return facts


def _dedupe_sources(sources: list[SourceFact]) -> list[SourceFact]:
    deduped: list[SourceFact] = []
    seen: set[tuple[str, str, str, str | None]] = set()
    for source in sources:
        key = (source.source, source.label, source.value, source.url)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(source)
    return deduped


def _tool_unavailable(warning: str) -> str:
    return json.dumps(
        {
            "status": "unavailable",
            "summary": warning,
            "source_facts": [],
            "warning": warning,
        }
    )
