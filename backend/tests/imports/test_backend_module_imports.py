import importlib


def test_backend_modules_import_without_cycles() -> None:
    for module_name in [
        "app.api.v1.dependencies",
        "app.api.v1.leads",
        "app.api.v1.agents",
        "app.api.v1.analytics",
        "app.agents.executors.signal_pipeline",
        "app.workers.tasks",
        "app.infrastructure.knowledge_graph.factory",
        "app.services.agent_execution_service",
        "app.services.lead_intake_service",
        "app.services.agent_run_service",
        "app.services.analytics_service",
        "app.repositories.signal_snapshot",
    ]:
        importlib.import_module(module_name)
