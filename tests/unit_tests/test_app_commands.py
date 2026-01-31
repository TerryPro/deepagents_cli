import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from deepagents_cli.app import DeepAgentsApp
from deepagents_cli.ui.messages import SystemMessage

@pytest.mark.asyncio
class TestSkillsCommand:
    async def test_skills_command_no_skills(self):
        """Test /skills command when no skills exist."""
        app = DeepAgentsApp()
        app._mount_message = AsyncMock()
        
        # Mock list_skills to return empty list
        with patch("deepagents_cli.skills.load.list_skills", return_value=[]), \
             patch("deepagents_cli.app.settings") as mock_settings:
            
            mock_settings.get_user_skills_dir.return_value = "user_dir"
            mock_settings.get_project_skills_dir.return_value = "project_dir"
            
            await app._handle_command("/skills")
            
            # Verify system message
            # The first call is UserMessage("/skills"), the second is SystemMessage
            assert app._mount_message.call_count == 2
            
            last_call_args = app._mount_message.call_args_list[-1]
            message = last_call_args[0][0]
            
            assert isinstance(message, SystemMessage)
            assert "No skills found" in message.content
            assert "Create your first skill" in message.content

    async def test_skills_command_with_skills(self):
        """Test /skills command with available skills."""
        app = DeepAgentsApp()
        app._mount_message = AsyncMock()
        
        mock_skills = [
            {"name": "user-skill", "description": "A user skill", "source": "user"},
            {"name": "project-skill", "description": "A project skill", "source": "project"},
        ]
        
        with patch("deepagents_cli.skills.load.list_skills", return_value=mock_skills), \
             patch("deepagents_cli.app.settings") as mock_settings:
                 
            await app._handle_command("/skills")
            
            # Verify system message
            assert app._mount_message.call_count == 2
            
            last_call_args = app._mount_message.call_args_list[-1]
            message = last_call_args[0][0]
            
            assert isinstance(message, SystemMessage)
            content = message.content
            
            assert "**Available Skills:**" in content
            assert "**User Skills:**" in content
            assert "**user-skill**: A user skill" in content
            assert "**Project Skills:**" in content
            assert "**project-skill**: A project skill" in content
