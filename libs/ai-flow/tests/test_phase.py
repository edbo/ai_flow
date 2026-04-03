"""Tests for the Phase base class."""

from __future__ import annotations

import pytest

from ai_flow.phases import InvalidTransitionError, Phase


class StubTarget(Phase):
    """A valid transition target for testing."""

    def _valid_transitions(self) -> set[type[Phase]]:
        return set()


class StubInvalid(Phase):
    """A phase that is not a valid target from StubPhase."""

    def _valid_transitions(self) -> set[type[Phase]]:
        return set()


class StubPhase(Phase):
    """A phase that can only transition to StubTarget."""

    def _valid_transitions(self) -> set[type[Phase]]:
        return {StubTarget}

    def advance(self) -> StubTarget:
        return self._transition(StubTarget)

    def advance_invalid(self) -> StubInvalid:
        return self._transition(StubInvalid)


class TestPhaseTransition:
    """Tests for Phase._transition()."""

    def test_transition_to_valid_target(self) -> None:
        phase = StubPhase()
        result = phase.advance()
        assert isinstance(result, StubTarget)

    def test_transition_to_invalid_target_raises(self) -> None:
        phase = StubPhase()
        with pytest.raises(InvalidTransitionError):
            phase.advance_invalid()
