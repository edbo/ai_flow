"""ImplementationApproval phase."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ai_flow.phases.base import Phase

if TYPE_CHECKING:
    from ai_flow.phases.completed import Completed
    from ai_flow.phases.implementation import Implementation


@dataclass(frozen=True)
class ImplementationApproval(Phase):
    """Human reviews the implementation."""

    def _valid_transitions(self) -> set[type[Phase]]:
        from ai_flow.phases.completed import Completed
        from ai_flow.phases.implementation import Implementation

        return {Completed, Implementation}

    def approve(self) -> Completed:
        from ai_flow.phases.completed import Completed

        return self._transition(Completed)

    def revise(self) -> Implementation:
        from ai_flow.phases.implementation import Implementation

        return self._transition(Implementation)
