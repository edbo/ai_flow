"""Backlog phase."""

from __future__ import annotations

from dataclasses import dataclass

from ai_flow.phases.base import Phase
from ai_flow.phases.planning import Planning


@dataclass(frozen=True)
class Backlog(Phase):
    """Initial phase — work not yet started."""

    def _valid_transitions(self) -> set[type[Phase]]:
        return {Planning}

    def start_planning(self) -> Planning:
        return self._transition(Planning)
