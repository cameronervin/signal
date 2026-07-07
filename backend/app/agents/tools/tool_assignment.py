"""Resolve active Signal research tools and prompt bindings."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from langchain_core.tools import BaseTool

from app.agents.tools.tool_prompts import TOOL_PROMPT_REGISTRY, ToolPromptKey
from app.agents.tools.tool_registry import (
    TOOL_REGISTRY,
    WORKFLOW_CHAIN_NAMES,
    ToolBuildContext,
    ToolSpec,
    ToolWorkflow,
)

WorkflowChainToolMap = dict[ToolWorkflow, dict[str, list[BaseTool]]]


def resolve_active_tools(
    config: object | ToolBuildContext,
    registry: Iterable[ToolSpec] = TOOL_REGISTRY,
) -> list[BaseTool]:
    """Build enabled model-callable tools in stable registry order."""
    context = (
        config if isinstance(config, ToolBuildContext) else ToolBuildContext(config)
    )
    tools: list[BaseTool] = []
    for spec in registry:
        if spec.enabled_predicate(context):
            tools.append(spec.factory(context))
    return tools


def build_workflow_chain_tool_map(
    active_tools: list[BaseTool],
    registry: Iterable[ToolSpec] = TOOL_REGISTRY,
) -> WorkflowChainToolMap:
    """Assign active tools to workflow and chain targets."""
    tool_by_name = {tool.name: tool for tool in active_tools}
    assignments: WorkflowChainToolMap = {
        workflow: {chain: [] for chain in chains}
        for workflow, chains in WORKFLOW_CHAIN_NAMES.items()
    }

    for spec in registry:
        tool = tool_by_name.get(spec.tool_name)
        if tool is None:
            continue
        for workflow, chain_names in spec.workflow_chain_targets.items():
            chain_map = assignments.setdefault(workflow, {})
            for chain_name in chain_names:
                chain_map.setdefault(chain_name, []).append(tool)
    return assignments


def build_prompt_bindings(
    active_tool_names: Iterable[str],
    registry: Iterable[ToolSpec] = TOOL_REGISTRY,
    prompt_registry: Mapping[ToolPromptKey, str] = TOOL_PROMPT_REGISTRY,
) -> dict[ToolPromptKey, str]:
    """Resolve prompt snippets for active tools."""
    active = set(active_tool_names)
    bindings: dict[ToolPromptKey, str] = {}
    for spec in registry:
        if spec.tool_name not in active:
            continue
        for prompt_key in spec.prompt_keys:
            snippet = prompt_registry.get(prompt_key)
            if snippet:
                bindings[prompt_key] = snippet
    return bindings
