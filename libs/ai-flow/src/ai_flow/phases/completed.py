"""Completed phase."""

from __future__ import annotations

from dataclasses import dataclass

from ai_flow.phases.base import Phase


@dataclass(frozen=True)
class Completed(Phase):
    """Terminal phase — work is done."""

    def _valid_transitions(self) -> set[type[Phase]]:
        return set()
