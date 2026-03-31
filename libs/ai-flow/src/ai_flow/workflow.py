"""Workflow state management."""

from dataclasses import dataclass, field


@dataclass
class Workflow:
    """Represents a workflow with a current state."""

    state: str = field(default="backlog")
