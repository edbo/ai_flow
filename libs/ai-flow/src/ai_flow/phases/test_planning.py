"""TestPlanning phase."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from ai_flow.phases.base import Phase

if TYPE_CHECKING:
    from ai_flow.phases.test_plan_approval import TestPlanApproval


@dataclass(frozen=True)
class TestPlanning(Phase):
    """Agent drafts a test plan."""

    __test__: ClassVar[bool] = False

    def _valid_transitions(self) -> set[type[Phase]]:
        from ai_flow.phases.test_plan_approval import TestPlanApproval

        return {TestPlanApproval}

    def submit_for_approval(self) -> TestPlanApproval:
        from ai_flow.phases.test_plan_approval import TestPlanApproval

        return self._transition(TestPlanApproval)
