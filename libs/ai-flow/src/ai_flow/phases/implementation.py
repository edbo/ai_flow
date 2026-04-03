"""Implementation phase."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ai_flow.phases.base import Phase

if TYPE_CHECKING:
    from ai_flow.phases.implementation_approval import ImplementationApproval


@dataclass(frozen=True)
class Implementation(Phase):
    """Agent implements the feature."""

    def _valid_transitions(self) -> set[type[Phase]]:
        from ai_flow.phases.implementation_approval import ImplementationApproval

        return {ImplementationApproval}

    def submit_for_approval(self) -> ImplementationApproval:
        from ai_flow.phases.implementation_approval import ImplementationApproval

        return self._transition(ImplementationApproval)
