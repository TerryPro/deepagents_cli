"""Message classes for skills modal communication.

This module defines message classes used for communication between
ChatInput, App, and SkillsModal components.
"""

from __future__ import annotations

from textual.message import Message


class ShowSkillsModal(Message):
    """Message sent from ChatInput to App to show skills modal.

    Attributes:
        agent: The agent identifier to show skills for.
    """

    def __init__(self, agent: str = "agent") -> None:
        """Initialize the message.

        Args:
            agent: The agent identifier (defaults to "agent").
        """
        self.agent = agent
        super().__init__()


class SkillsSelected(Message):
    """Message sent from SkillsModal to App when a skill is selected.

    Attributes:
        skill_name: The name of the selected skill.
    """

    def __init__(self, skill_name: str) -> None:
        """Initialize the message.

        Args:
            skill_name: The name of the selected skill.
        """
        self.skill_name = skill_name
        super().__init__()


class SkillsCancelled(Message):
    """Message sent from SkillsModal to App when cancelled."""

    def __init__(self) -> None:
        """Initialize the message."""
        super().__init__()
