from typing import Any

from langgraph.runtime import Runtime

from app.agents.chains.digital_worker import DIGITAL_WORKER_DECISION_CHAIN
from app.agents.runtime_context import DigitalWorkerRuntimeContext
from app.agents.states.digital_worker_state import DigitalWorkerState
from app.agents.tools.digital_worker import (
    DIGITAL_WORKER_MARK_GOAL_COMPLETE_TOOL,
    DIGITAL_WORKER_MARK_PHASE_OUTCOME_TOOL,
    DIGITAL_WORKER_SCHEDULE_FOLLOW_UP_TOOL,
    DIGITAL_WORKER_SEND_SANDBOX_EMAIL_TOOL,
    DigitalWorkerTools,
)

DIGITAL_WORKER_CONTEXT_NODE = "digital_worker_context"
DIGITAL_WORKER_ACTION_NODE = "digital_worker_action"


def create_digital_worker_nodes(*, chains: dict[str, Any]) -> dict[str, Any]:
    async def load_worker_context(
        state: DigitalWorkerState,
        runtime: Runtime[DigitalWorkerRuntimeContext],
    ) -> dict[str, Any]:
        run = await runtime.context.worker_repository.get_run(state["run_id"])
        if run is None:
            raise ValueError("Digital worker run not found")
        assignment = await runtime.context.worker_repository.get_assignment(
            run.assignment_id
        )
        if assignment is None:
            raise ValueError("Digital worker assignment not found")
        lead = await runtime.context.signal_repository.get_lead(assignment.lead_id)
        if lead is None:
            raise ValueError("Assigned lead snapshot not found")
        return {
            "assignment_id": assignment.assignment_id,
            "trigger": run.trigger,
            "run": run,
            "assignment": assignment,
            "lead": lead,
            "activity_log": ["digital_worker_context: loaded"],
        }

    async def execute_worker_action(
        state: DigitalWorkerState,
        runtime: Runtime[DigitalWorkerRuntimeContext],
    ) -> dict[str, Any]:
        decision = await chains[DIGITAL_WORKER_DECISION_CHAIN].ainvoke(
            {
                "assignment": state["assignment"],
                "lead": state["lead"],
                "lifecycle": runtime.context.lifecycle,
                "trigger": state["trigger"],
            },
            config={"configurable": {"run_id": str(state["run_id"])}},
        )
        tools = DigitalWorkerTools(runtime.context.worker_repository)
        for action in decision.actions:
            await _execute_tool_action(tools, action.tool_name, action.arguments)
        return {
            "activity_log": [
                *state.get("activity_log", []),
                f"digital_worker_action: {decision.activity}",
            ]
        }

    return {
        DIGITAL_WORKER_CONTEXT_NODE: load_worker_context,
        DIGITAL_WORKER_ACTION_NODE: execute_worker_action,
    }


async def _execute_tool_action(
    tools: DigitalWorkerTools,
    tool_name: str,
    arguments: dict[str, Any],
) -> None:
    if tool_name == DIGITAL_WORKER_SEND_SANDBOX_EMAIL_TOOL:
        await tools.send_sandbox_email(**arguments)
        return
    if tool_name == DIGITAL_WORKER_SCHEDULE_FOLLOW_UP_TOOL:
        await tools.schedule_follow_up(**arguments)
        return
    if tool_name == DIGITAL_WORKER_MARK_GOAL_COMPLETE_TOOL:
        await tools.mark_goal_complete(**arguments)
        return
    if tool_name == DIGITAL_WORKER_MARK_PHASE_OUTCOME_TOOL:
        await tools.mark_phase_outcome(**arguments)
        return
    raise ValueError(f"Unknown digital worker tool: {tool_name}")
