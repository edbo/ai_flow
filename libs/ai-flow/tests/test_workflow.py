"""Tests for the Workflow class."""

from ai_flow.workflow import Workflow


class TestWorkflow:
    """Tests for Workflow state management."""

    def test_default_state_is_backlog(self) -> None:
        workflow = Workflow()
        assert workflow.state == "backlog"
