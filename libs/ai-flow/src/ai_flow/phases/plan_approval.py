"""PlanApproval phase."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ai_flow.phases.base import Phase

if TYPE_CHECKING:
    from ai_flow.phases.planning import Planning
    from ai_flow.phases.test_planning import TestPlanning


@dataclass(frozen=True)
class PlanApproval(Phase):
    """Human reviews the implementation plan."""

    def _valid_transitions(self) -> set[type[Phase]]:
        from ai_flow.phases.planning import Planning
        from ai_flow.phases.test_planning import TestPlanning

        return {TestPlanning, Planning}

    def approve(self) -> TestPlanning:
        from ai_flow.phases.test_planning import TestPlanning

        return self._transition(TestPlanning)

    def revise(self) -> Planning:
        from ai_flow.phases.planning import Planning

        return self._transition(Planning)
