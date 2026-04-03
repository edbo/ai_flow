"""Planning phase."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ai_flow.phases.base import Phase

if TYPE_CHECKING:
    from ai_flow.phases.plan_approval import PlanApproval


@dataclass(frozen=True)
class Planning(Phase):
    """Agent drafts an implementation plan."""

    def _valid_transitions(self) -> set[type[Phase]]:
        from ai_flow.phases.plan_approval import PlanApproval

        return {PlanApproval}

    def submit_for_approval(self) -> PlanApproval:
        from ai_flow.phases.plan_approval import PlanApproval

        return self._transition(PlanApproval)
