"""Signal agent runtime packages.

Package shape follows the Playbook-inspired direction, but each module is named
for the one bounded lead-intelligence workflow Signal needs in v1.
"""

from app.agents.executors.signal_pipeline import SignalPipelineExecutor
from app.agents.states.signal_state import SignalState

__all__ = ["SignalPipelineExecutor", "SignalState"]
