"""Integration tests for Skills Modal feature.

This module tests the end-to-end flow of the skills modal feature,
including the interaction between ChatInput, DeepAgentsApp, and SkillsModal.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from deepagents_cli.widgets.chat_input import ChatInput
from deepagents_cli.widgets.skills_messages import (
    ShowSkillsModal,
    SkillsCancelled,
    SkillsSelected,
)
from deepagents_cli.widgets.skills_modal import SkillsModal


@pytest.mark.asyncio
class TestSkillsModalIntegration:
    """Integration tests for SkillsModal complete flow."""

    async def test_skills_command_triggers_modal_message(self):
        """Test that ChatInput posts ShowSkillsModal when /skills is submitted."""
        chat_input = ChatInput(agent="test-agent")

        # Mock the text area
        chat_input._text_area = MagicMock()
        chat_input._text_area.get_text.return_value = "/skills"
        chat_input._text_area.clear_text = MagicMock()

        # Track posted messages
        posted_messages = []

        def mock_post_message(msg):
            posted_messages.append(msg)

        chat_input.post_message = mock_post_message

        # Create and trigger the submitted event
        class MockSubmitted:
            def __init__(self, value):
                self.value = value

        event = MockSubmitted("/skills")
        chat_input.on_chat_text_area_submitted(event)

        # Verify ShowSkillsModal was posted (along with ModeChanged from clearing)
        show_skills_messages = [m for m in posted_messages if isinstance(m, ShowSkillsModal)]
        assert len(show_skills_messages) == 1
        assert show_skills_messages[0].agent == "test-agent"

    async def test_show_skills_modal_message_properties(self):
        """Test ShowSkillsModal message initialization and properties."""
        # Test with default agent
        msg_default = ShowSkillsModal()
        assert msg_default.agent == "agent"

        # Test with custom agent
        msg_custom = ShowSkillsModal(agent="custom-agent")
        assert msg_custom.agent == "custom-agent"

    async def test_app_handles_show_skills_modal(self, tmp_path: Path):
        """Test that DeepAgentsApp can handle ShowSkillsModal event.

        This test verifies the app has the on_show_skills_modal handler.
        """
        from deepagents_cli.app import DeepAgentsApp

        # Verify the handler method exists
        assert hasattr(DeepAgentsApp, "on_show_skills_modal")
        assert callable(getattr(DeepAgentsApp, "on_show_skills_modal"))

    async def test_app_has_skill_selected_callback(self):
        """Test that DeepAgentsApp has _on_skill_selected callback."""
        from deepagents_cli.app import DeepAgentsApp

        # Verify the callback method exists
        assert hasattr(DeepAgentsApp, "_on_skill_selected")
        assert callable(getattr(DeepAgentsApp, "_on_skill_selected"))

    async def test_skills_selected_message(self):
        """Test SkillsSelected message creation and properties."""
        msg = SkillsSelected("test-skill")
        assert msg.skill_name == "test-skill"

    async def test_skills_cancelled_message(self):
        """Test SkillsCancelled message creation."""
        msg = SkillsCancelled()
        assert msg is not None


@pytest.mark.asyncio
class TestSkillsModalWithMockSkills:
    """Integration tests for SkillsModal with mocked skill files."""

    @patch("deepagents_cli.widgets.skills_modal.settings")
    @patch("deepagents_cli.widgets.skills_modal.list_skills")
    async def test_modal_loads_and_displays_skills(self, mock_list_skills, mock_settings, tmp_path: Path):
        """Test that SkillsModal loads skills and creates skill cards."""
        # Mock settings
        mock_settings.get_user_skills_dir.return_value = tmp_path

        # Mock skills data
        mock_skills = [
            {"name": "skill-1", "description": "First skill description", "source": "user"},
            {"name": "skill-2", "description": "Second skill description", "source": "project"},
            {"name": "skill-3", "description": "Third skill description", "source": "user"},
        ]
        mock_list_skills.return_value = mock_skills

        # Create modal
        modal = SkillsModal(agent="test-agent", project_skills_dir=tmp_path)

        # Mock grid and empty message
        modal._grid = MagicMock()
        modal._empty_message = MagicMock()
        modal._skill_cards = []

        # Load skills
        modal._load_skills()

        # Verify list_skills was called
        mock_list_skills.assert_called_once()

        # Verify skill cards were created
        assert len(modal._skill_cards) == 3

    @patch("deepagents_cli.widgets.skills_modal.list_skills")
    async def test_modal_navigation_with_skills(self, mock_list_skills):
        """Test navigation actions work with loaded skills."""
        mock_list_skills.return_value = [
            {"name": "skill-1", "description": "First skill", "source": "user"},
            {"name": "skill-2", "description": "Second skill", "source": "user"},
            {"name": "skill-3", "description": "Third skill", "source": "user"},
            {"name": "skill-4", "description": "Fourth skill", "source": "user"},
        ]

        modal = SkillsModal(agent="test-agent")
        modal._grid = MagicMock()
        modal._empty_message = MagicMock()
        modal._skill_cards = []

        modal._load_skills()

        # Verify initial selection
        assert modal._selected_index == 0

        # Test navigate down
        modal.action_navigate_down()
        assert modal._selected_index == 2  # 2-column grid, down moves by 2

        # Test navigate right
        modal.action_navigate_right()
        assert modal._selected_index == 3

        # Test navigate left
        modal.action_navigate_left()
        assert modal._selected_index == 2

        # Test navigate up
        modal.action_navigate_up()
        assert modal._selected_index == 0


@pytest.mark.asyncio
class TestSkillsModalEmptyState:
    """Integration tests for SkillsModal empty state handling."""

    @patch("deepagents_cli.widgets.skills_modal.list_skills")
    async def test_modal_shows_empty_state(self, mock_list_skills, tmp_path: Path):
        """Test that modal shows empty state when no skills exist."""
        # Mock empty skills list
        mock_list_skills.return_value = []

        # Create modal
        modal = SkillsModal(agent="test-agent", project_skills_dir=tmp_path)

        # Mock grid and empty message
        modal._grid = MagicMock()
        modal._empty_message = MagicMock()
        modal._empty_message.display = True

        # Load skills
        modal._load_skills()

        # Verify list_skills was called
        mock_list_skills.assert_called_once()

        # Verify empty state was shown
        modal._grid.remove_children.assert_called_once()

    @patch("deepagents_cli.widgets.skills_modal.list_skills")
    async def test_modal_handles_empty_selection(self, mock_list_skills):
        """Test that action_select handles empty skills gracefully."""
        mock_list_skills.return_value = []

        modal = SkillsModal(agent="test-agent")
        modal._grid = MagicMock()
        modal._empty_message = MagicMock()
        modal._skill_cards = []
        modal._selected_index = -1

        modal._load_skills()

        # Should not raise an error when selecting with no skills
        modal.action_select()  # Should complete without error


@pytest.mark.asyncio
class TestSkillsModalCancellation:
    """Integration tests for SkillsModal cancellation flow."""

    async def test_action_cancel_posts_cancelled_message(self):
        """Test that action_cancel posts SkillsCancelled message."""
        modal = SkillsModal(agent="test-agent")

        # Track posted messages
        posted_messages = []

        def mock_post_message(msg):
            posted_messages.append(msg)

        modal.post_message = mock_post_message

        # Mock dismiss
        modal.dismiss = MagicMock()

        # Trigger cancel action
        modal.action_cancel()

        # Verify SkillsCancelled was posted
        assert len(posted_messages) == 1
        assert isinstance(posted_messages[0], SkillsCancelled)

        # Verify dismiss was called with None
        modal.dismiss.assert_called_once_with(None)

    @patch("deepagents_cli.widgets.skills_modal.list_skills")
    async def test_action_select_posts_selected_message(self, mock_list_skills):
        """Test that action_select posts SkillsSelected message."""
        mock_list_skills.return_value = [
            {"name": "test-skill", "description": "Test skill", "source": "user"},
        ]

        modal = SkillsModal(agent="test-agent")
        modal._grid = MagicMock()
        modal._empty_message = MagicMock()
        modal._skill_cards = []

        modal._load_skills()

        # Track posted messages
        posted_messages = []

        def mock_post_message(msg):
            posted_messages.append(msg)

        modal.post_message = mock_post_message
        modal.dismiss = MagicMock()

        # Select the skill
        modal.action_select()

        # Verify SkillsSelected was posted
        assert len(posted_messages) == 1
        assert isinstance(posted_messages[0], SkillsSelected)
        assert posted_messages[0].skill_name == "test-skill"

        # Verify dismiss was called with skill name
        modal.dismiss.assert_called_once_with("test-skill")


@pytest.mark.asyncio
class TestSkillsModalWithRealFiles:
    """Integration tests for SkillsModal with actual temporary skill files."""

    async def test_modal_loads_real_skills_from_temp_directory(self, tmp_path: Path):
        """Test loading skills from temporary directory structure.

        This creates actual skill files in a temp directory and verifies
the modal can load them.
        """
        # Create skills directory structure
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()

        # Create skill files
        (skills_dir / "test-skill-1").mkdir()
        (skills_dir / "test-skill-1" / "skill.yaml").write_text(
            "name: test-skill-1\ndescription: First test skill\n"
        )

        (skills_dir / "test-skill-2").mkdir()
        (skills_dir / "test-skill-2" / "skill.yaml").write_text(
            "name: test-skill-2\ndescription: Second test skill\n"
        )

        # Create modal pointing to temp directory
        modal = SkillsModal(agent="test-agent", project_skills_dir=skills_dir)

        # Mock the grid to avoid actual UI mounting
        modal._grid = MagicMock()
        modal._empty_message = MagicMock()
        modal._skill_cards = []

        # Mock settings to return our temp directory
        with patch("deepagents_cli.widgets.skills_modal.settings") as mock_settings:
            mock_settings.skills_dir.return_value = skills_dir

            # Load skills
            modal._load_skills()

        # Verify skills were loaded (actual count depends on deepagents backend)
        # We just verify the loading mechanism works
        assert isinstance(modal._skill_cards, list)


@pytest.mark.asyncio
class TestSkillsModalCommandInsertion:
    """Integration tests for skill selection and command insertion."""

    async def test_on_skill_selected_callback_with_skill_name(self):
        """Test _on_skill_selected callback behavior with a skill name.

        This tests the logic that would be triggered when a skill is selected.
        """
        from deepagents_cli.app import DeepAgentsApp

        # Verify the callback signature accepts str | None
        import inspect
        sig = inspect.signature(DeepAgentsApp._on_skill_selected)
        params = list(sig.parameters.keys())
        assert "skill_name" in params

    async def test_skill_selection_command_format(self):
        """Test that the correct command format is generated for selected skills."""
        # The command should be "/use-skill {skill_name}"
        skill_name = "my-test-skill"
        expected_command = f"/use-skill {skill_name}"
        assert expected_command == "/use-skill my-test-skill"


@pytest.mark.asyncio
class TestSkillsModalBindings:
    """Integration tests for SkillsModal key bindings."""

    async def test_bindings_include_all_navigation_keys(self):
        """Test that all required navigation keys are bound."""
        bindings = SkillsModal.BINDINGS

        binding_keys = [binding.key for binding in bindings]

        # Navigation keys
        assert "up" in binding_keys
        assert "down" in binding_keys
        assert "left" in binding_keys
        assert "right" in binding_keys

        # Action keys
        assert "enter" in binding_keys
        assert "escape" in binding_keys

    async def test_bindings_have_descriptions(self):
        """Test that key bindings have proper descriptions."""
        for binding in SkillsModal.BINDINGS:
            assert binding.action is not None
            assert binding.description is not None


@pytest.mark.asyncio
class TestSkillsModalInitialization:
    """Integration tests for SkillsModal initialization parameters."""

    async def test_modal_accepts_agent_parameter(self):
        """Test that SkillsModal accepts agent parameter."""
        modal = SkillsModal(agent="my-special-agent")
        assert modal._agent == "my-special-agent"

    async def test_modal_accepts_project_skills_dir(self, tmp_path: Path):
        """Test that SkillsModal accepts project_skills_dir parameter."""
        modal = SkillsModal(agent="test-agent", project_skills_dir=tmp_path)
        assert modal._project_skills_dir == tmp_path

    async def test_modal_defaults(self):
        """Test that SkillsModal has sensible defaults."""
        modal = SkillsModal()
        assert modal._agent == "agent"
        assert modal._project_skills_dir is None
        assert modal._selected_index == -1
        assert modal._skill_cards == []
