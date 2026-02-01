"""Unit tests for SkillsModal screen."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from deepagents_cli.widgets.skills_modal import SkillsModal
from deepagents_cli.widgets.skills_messages import SkillsCancelled, SkillsSelected


class TestSkillsModal:
    """Test suite for SkillsModal screen."""

    def test_skills_modal_inherits_from_modal_screen(self):
        """Test that SkillsModal inherits from ModalScreen."""
        assert "ModalScreen" in [base.__name__ for base in SkillsModal.__bases__]

    def test_skills_modal_constructor_accepts_agent(self):
        """Test that SkillsModal accepts agent parameter in constructor."""
        modal = SkillsModal(agent="my-agent")
        assert modal is not None

    def test_skills_modal_constructor_accepts_project_skills_dir(self):
        """Test that SkillsModal accepts project_skills_dir parameter."""
        modal = SkillsModal(agent="agent", project_skills_dir=Path("/some/path"))
        assert modal is not None

    def test_skills_modal_has_default_css(self):
        """Test that SkillsModal has DEFAULT_CSS attribute."""
        assert hasattr(SkillsModal, "DEFAULT_CSS")
        assert isinstance(SkillsModal.DEFAULT_CSS, str)

    def test_default_css_has_modal_styling(self):
        """Test that DEFAULT_CSS contains modal styling."""
        css = SkillsModal.DEFAULT_CSS
        assert "width" in css.lower()
        assert "height" in css.lower()

    def test_skills_modal_has_bindings(self):
        """Test that SkillsModal has key bindings defined."""
        assert hasattr(SkillsModal, "BINDINGS")
        bindings = SkillsModal.BINDINGS
        assert len(bindings) > 0

    def test_bindings_include_navigation(self):
        """Test that bindings include arrow key navigation."""
        bindings = SkillsModal.BINDINGS
        binding_keys = [binding.key for binding in bindings]
        assert "up" in binding_keys
        assert "down" in binding_keys
        assert "left" in binding_keys
        assert "right" in binding_keys

    def test_bindings_include_selection(self):
        """Test that bindings include selection keys."""
        bindings = SkillsModal.BINDINGS
        binding_keys = [binding.key for binding in bindings]
        assert "enter" in binding_keys
        assert "escape" in binding_keys

    def test_skills_modal_has_compose_method(self):
        """Test that SkillsModal has compose method."""
        assert hasattr(SkillsModal, "compose")

    def test_skills_modal_has_on_mount_method(self):
        """Test that SkillsModal has on_mount method."""
        assert hasattr(SkillsModal, "on_mount")

    def test_skills_modal_has_load_skills_method(self):
        """Test that SkillsModal has _load_skills method."""
        assert hasattr(SkillsModal, "_load_skills")

    def test_skills_modal_has_update_selection_method(self):
        """Test that SkillsModal has _update_selection method."""
        assert hasattr(SkillsModal, "_update_selection")

    def test_skills_modal_has_navigate_methods(self):
        """Test that SkillsModal has navigation action methods."""
        assert hasattr(SkillsModal, "action_navigate_up")
        assert hasattr(SkillsModal, "action_navigate_down")
        assert hasattr(SkillsModal, "action_navigate_left")
        assert hasattr(SkillsModal, "action_navigate_right")

    def test_skills_modal_has_select_method(self):
        """Test that SkillsModal has action_select method."""
        assert hasattr(SkillsModal, "action_select")

    def test_skills_modal_has_cancel_method(self):
        """Test that SkillsModal has action_cancel method."""
        assert hasattr(SkillsModal, "action_cancel")

    def test_skills_modal_has_on_click_method(self):
        """Test that SkillsModal has on_click method."""
        assert hasattr(SkillsModal, "on_click")


class TestSkillsModalIntegration:
    """Integration tests for SkillsModal with mocks."""

    @patch("deepagents_cli.widgets.skills_modal.list_skills")
    def test_load_skills_displays_cards(self, mock_list_skills):
        """Test that _load_skills creates skill cards."""
        # Mock return value
        mock_list_skills.return_value = [
            {"name": "skill-1", "description": "First skill", "source": "user"},
            {"name": "skill-2", "description": "Second skill", "source": "project"},
        ]

        modal = SkillsModal(agent="agent")
        # Manually set up the widgets dict to simulate compose
        modal._skill_cards = []
        modal._list = MagicMock()
        modal._empty_message = MagicMock()

        # Call _load_skills
        modal._load_skills()

        # Verify list_skills was called
        mock_list_skills.assert_called_once()

    @patch("deepagents_cli.widgets.skills_modal.list_skills")
    def test_load_skills_shows_empty_state(self, mock_list_skills):
        """Test that empty skills list shows empty state message."""
        mock_list_skills.return_value = []

        modal = SkillsModal(agent="agent")
        modal._skill_cards = []
        modal._list = MagicMock()
        modal._empty_message = MagicMock()

        modal._load_skills()

        # Verify empty message was displayed
        modal._empty_message.update.assert_called()

    def test_action_select_with_no_selection(self):
        """Test that action_select handles no selection gracefully."""
        modal = SkillsModal(agent="agent")
        modal._selected_index = -1
        modal._skill_cards = []

        # Should not raise error
        modal.action_select()

    def test_action_cancel_posts_cancelled_message(self):
        """Test that action_cancel posts SkillsCancelled message."""
        modal = SkillsModal(agent="agent")
        
        with patch.object(modal, "post_message") as mock_post:
            modal.action_cancel()
            mock_post.assert_called_once()
            args = mock_post.call_args[0]
            assert isinstance(args[0], SkillsCancelled)

    def test_get_agent_returns_agent_name(self):
        """Test that _agent attribute stores the agent name."""
        modal = SkillsModal(agent="my-agent")
        assert modal._agent == "my-agent"

    def test_get_project_skills_dir_returns_path(self):
        """Test that _project_skills_dir attribute stores the path."""
        path = Path("/test/path")
        modal = SkillsModal(agent="agent", project_skills_dir=path)
        assert modal._project_skills_dir == path
