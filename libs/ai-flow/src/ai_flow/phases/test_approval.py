"""TestApproval phase."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from ai_flow.phases.base import Phase

if TYPE_CHECKING:
    from ai_flow.phases.implementation import Implementation
    from ai_flow.phases.test_implementation import TestImplementation


@dataclass(frozen=True)
class TestApproval(Phase):
    """Human reviews tests."""

    __test__: ClassVar[bool] = False

    def _valid_transitions(self) -> set[type[Phase]]:
        from ai_flow.phases.implementation import Implementation
        from ai_flow.phases.test_implementation import TestImplementation

        return {Implementation, TestImplementation}

    def approve(self) -> Implementation:
        from ai_flow.phases.implementation import Implementation

        return self._transition(Implementation)

    def revise(self) -> TestImplementation:
        from ai_flow.phases.test_implementation import TestImplementation

        return self._transition(TestImplementation)
