"""TestPlanApproval phase."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from ai_flow.phases.base import Phase

if TYPE_CHECKING:
    from ai_flow.phases.test_implementation import TestImplementation
    from ai_flow.phases.test_planning import TestPlanning


@dataclass(frozen=True)
class TestPlanApproval(Phase):
    """Human reviews the test plan."""

    __test__: ClassVar[bool] = False

    def _valid_transitions(self) -> set[type[Phase]]:
        from ai_flow.phases.test_implementation import TestImplementation
        from ai_flow.phases.test_planning import TestPlanning

        return {TestImplementation, TestPlanning}

    def approve(self) -> TestImplementation:
        from ai_flow.phases.test_implementation import TestImplementation

        return self._transition(TestImplementation)

    def revise(self) -> TestPlanning:
        from ai_flow.phases.test_planning import TestPlanning

        return self._transition(TestPlanning)
