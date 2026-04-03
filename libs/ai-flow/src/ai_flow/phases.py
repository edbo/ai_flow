"""Workflow phase base class and transition logic."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypeVar

_P = TypeVar("_P", bound="Phase")


class InvalidTransitionError(Exception):
    """Raised when a phase transition is not allowed."""


@dataclass(frozen=True)
class Phase(ABC):
    """Abstract base class for workflow phases."""

    @abstractmethod
    def _valid_transitions(self) -> set[type[Phase]]:
        """Return the set of phase types this phase can transition to."""

    def _transition(self, target: type[_P]) -> _P:
        """Validate and perform a transition, returning a new Phase instance."""
        if target not in self._valid_transitions():
            raise InvalidTransitionError(f"Cannot transition from {type(self).__name__} to {target.__name__}")
        return target()
