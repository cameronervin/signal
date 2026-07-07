"""Declarative registry of Signal agent research tools."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal

from langchain_core.tools import BaseTool

from app.agents.chains.outreach_drafting import OUTREACH_DRAFT_CHAIN
from app.agents.tools.public_data import (
    create_census_tool,
    create_datausa_tool,
    create_domain_tool,
    create_fred_tool,
    create_geocoding_tool,
    create_news_tool,
    create_wikipedia_tool,
    enrich_lead_with_public_data,
)
from app.agents.tools.tool_prompts import ToolPromptKey

PUBLIC_DATA_ENRICHMENT_TOOL = "public_data_enrichment"

ToolWorkflow = Literal["signal_pipeline"]

WORKFLOW_CHAIN_NAMES: dict[ToolWorkflow, tuple[str, ...]] = {
    "signal_pipeline": (OUTREACH_DRAFT_CHAIN,),
}


@dataclass(slots=True)
class ToolBuildContext:
    """Settings available while constructing model-callable tools."""

    settings: object


@dataclass(frozen=True, slots=True)
class ToolSpec:
    """Declarative model-callable tool registration."""

    tool_name: str
    factory: Callable[[ToolBuildContext], BaseTool]
    enabled_predicate: Callable[[ToolBuildContext], bool]
    workflow_chain_targets: Mapping[ToolWorkflow, Sequence[str]]
    prompt_keys: Sequence[ToolPromptKey] = ()


def create_signal_tool_set() -> dict[str, Any]:
    """Return deterministic node tools used by the Signal pipeline."""
    return {PUBLIC_DATA_ENRICHMENT_TOOL: enrich_lead_with_public_data}


def _research_tools_enabled(context: ToolBuildContext) -> bool:
    return bool(getattr(context.settings, "agent_research_tools_enabled", True))


def _fred_enabled(context: ToolBuildContext) -> bool:
    return _research_tools_enabled(context) and bool(
        getattr(context.settings, "fred_api_key", None)
    )


def _news_enabled(context: ToolBuildContext) -> bool:
    return _research_tools_enabled(context) and bool(
        getattr(context.settings, "news_api_key", None)
    )


def _create_geocoding_tool(_context: ToolBuildContext) -> BaseTool:
    return create_geocoding_tool()


def _create_census_tool(_context: ToolBuildContext) -> BaseTool:
    return create_census_tool()


def _create_datausa_tool(_context: ToolBuildContext) -> BaseTool:
    return create_datausa_tool()


def _create_fred_tool(_context: ToolBuildContext) -> BaseTool:
    return create_fred_tool()


def _create_news_tool(_context: ToolBuildContext) -> BaseTool:
    return create_news_tool()


def _create_wikipedia_tool(_context: ToolBuildContext) -> BaseTool:
    return create_wikipedia_tool()


def _create_domain_tool(_context: ToolBuildContext) -> BaseTool:
    return create_domain_tool()


def _outreach_prompt(tool_name: str) -> tuple[ToolPromptKey, ...]:
    return (ToolPromptKey(OUTREACH_DRAFT_CHAIN, tool_name),)


def _outreach_target() -> Mapping[ToolWorkflow, Sequence[str]]:
    return {"signal_pipeline": (OUTREACH_DRAFT_CHAIN,)}


TOOL_REGISTRY: tuple[ToolSpec, ...] = (
    ToolSpec(
        tool_name="geocode_property_address",
        factory=_create_geocoding_tool,
        enabled_predicate=_research_tools_enabled,
        workflow_chain_targets=_outreach_target(),
        prompt_keys=_outreach_prompt("geocode_property_address"),
    ),
    ToolSpec(
        tool_name="fetch_census_market_demographics",
        factory=_create_census_tool,
        enabled_predicate=_research_tools_enabled,
        workflow_chain_targets=_outreach_target(),
        prompt_keys=_outreach_prompt("fetch_census_market_demographics"),
    ),
    ToolSpec(
        tool_name="fetch_datausa_household_growth",
        factory=_create_datausa_tool,
        enabled_predicate=_research_tools_enabled,
        workflow_chain_targets=_outreach_target(),
        prompt_keys=_outreach_prompt("fetch_datausa_household_growth"),
    ),
    ToolSpec(
        tool_name="fetch_fred_market_economics",
        factory=_create_fred_tool,
        enabled_predicate=_fred_enabled,
        workflow_chain_targets=_outreach_target(),
        prompt_keys=_outreach_prompt("fetch_fred_market_economics"),
    ),
    ToolSpec(
        tool_name="lookup_news_company_trigger",
        factory=_create_news_tool,
        enabled_predicate=_news_enabled,
        workflow_chain_targets=_outreach_target(),
        prompt_keys=_outreach_prompt("lookup_news_company_trigger"),
    ),
    ToolSpec(
        tool_name="lookup_wikipedia_company_background",
        factory=_create_wikipedia_tool,
        enabled_predicate=_research_tools_enabled,
        workflow_chain_targets=_outreach_target(),
        prompt_keys=_outreach_prompt("lookup_wikipedia_company_background"),
    ),
    ToolSpec(
        tool_name="validate_email_domain_mx",
        factory=_create_domain_tool,
        enabled_predicate=_research_tools_enabled,
        workflow_chain_targets=_outreach_target(),
        prompt_keys=_outreach_prompt("validate_email_domain_mx"),
    ),
)
