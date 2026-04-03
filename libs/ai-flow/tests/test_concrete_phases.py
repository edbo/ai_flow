"""Tests for concrete phase classes."""

from __future__ import annotations

import pytest

from ai_flow.phases import (
    Backlog,
    Completed,
    Implementation,
    ImplementationApproval,
    InvalidTransitionError,
    PlanApproval,
    Planning,
    TestApproval,
    TestImplementation,
    TestPlanApproval,
    TestPlanning,
)


class TestBacklogPhase:
    """Tests for the Backlog phase."""

    def test_start_planning_returns_planning(self) -> None:
        result = Backlog().start_planning()
        assert isinstance(result, Planning)

    def test_is_frozen(self) -> None:
        with pytest.raises(AttributeError):
            Backlog().x = 1  # type: ignore[attr-defined]


class TestPlanningPhase:
    """Tests for the Planning phase."""

    def test_submit_for_approval_returns_plan_approval(self) -> None:
        result = Planning().submit_for_approval()
        assert isinstance(result, PlanApproval)


class TestPlanApprovalPhase:
    """Tests for the PlanApproval phase."""

    def test_approve_returns_test_planning(self) -> None:
        result = PlanApproval().approve()
        assert isinstance(result, TestPlanning)

    def test_revise_returns_planning(self) -> None:
        result = PlanApproval().revise()
        assert isinstance(result, Planning)


class TestTestPlanningPhase:
    """Tests for the TestPlanning phase."""

    def test_submit_for_approval_returns_test_plan_approval(self) -> None:
        result = TestPlanning().submit_for_approval()
        assert isinstance(result, TestPlanApproval)


class TestTestPlanApprovalPhase:
    """Tests for the TestPlanApproval phase."""

    def test_approve_returns_test_implementation(self) -> None:
        result = TestPlanApproval().approve()
        assert isinstance(result, TestImplementation)

    def test_revise_returns_test_planning(self) -> None:
        result = TestPlanApproval().revise()
        assert isinstance(result, TestPlanning)


class TestTestImplementationPhase:
    """Tests for the TestImplementation phase."""

    def test_submit_for_approval_returns_test_approval(self) -> None:
        result = TestImplementation().submit_for_approval()
        assert isinstance(result, TestApproval)


class TestTestApprovalPhase:
    """Tests for the TestApproval phase."""

    def test_approve_returns_implementation(self) -> None:
        result = TestApproval().approve()
        assert isinstance(result, Implementation)

    def test_revise_returns_test_implementation(self) -> None:
        result = TestApproval().revise()
        assert isinstance(result, TestImplementation)


class TestImplementationPhase:
    """Tests for the Implementation phase."""

    def test_submit_for_approval_returns_implementation_approval(self) -> None:
        result = Implementation().submit_for_approval()
        assert isinstance(result, ImplementationApproval)


class TestImplementationApprovalPhase:
    """Tests for the ImplementationApproval phase."""

    def test_approve_returns_completed(self) -> None:
        result = ImplementationApproval().approve()
        assert isinstance(result, Completed)

    def test_revise_returns_implementation(self) -> None:
        result = ImplementationApproval().revise()
        assert isinstance(result, Implementation)


class TestCompletedPhase:
    """Tests for the Completed phase."""

    def test_is_terminal(self) -> None:
        assert Completed()._valid_transitions() == set()


class TestFullWorkflow:
    """Test the complete happy-path workflow from Backlog to Completed."""

    def test_happy_path(self) -> None:
        phase = Backlog()
        phase2 = phase.start_planning()
        phase3 = phase2.submit_for_approval()
        phase4 = phase3.approve()
        phase5 = phase4.submit_for_approval()
        phase6 = phase5.approve()
        phase7 = phase6.submit_for_approval()
        phase8 = phase7.approve()
        phase9 = phase8.submit_for_approval()
        result = phase9.approve()
        assert isinstance(result, Completed)

    def test_revise_loop(self) -> None:
        """Plan gets rejected, revised, then approved."""
        phase = PlanApproval()
        revised = phase.revise()
        assert isinstance(revised, Planning)
        resubmitted = revised.submit_for_approval()
        assert isinstance(resubmitted, PlanApproval)
        approved = resubmitted.approve()
        assert isinstance(approved, TestPlanning)

    def test_invalid_transition_raises(self) -> None:
        with pytest.raises(InvalidTransitionError):
            Completed()._transition(Backlog)
