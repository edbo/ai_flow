"""TestImplementation phase."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from ai_flow.phases.base import Phase

if TYPE_CHECKING:
    from ai_flow.phases.test_approval import TestApproval


@dataclass(frozen=True)
class TestImplementation(Phase):
    """Agent implements tests."""

    __test__: ClassVar[bool] = False

    def _valid_transitions(self) -> set[type[Phase]]:
        from ai_flow.phases.test_approval import TestApproval

        return {TestApproval}

    def submit_for_approval(self) -> TestApproval:
        from ai_flow.phases.test_approval import TestApproval

        return self._transition(TestApproval)
