"""SkillsModal screen for browsing and selecting skills.

This module provides a modal screen for displaying all available skills
in a simple list view with keyboard and mouse navigation.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Label, ListItem, ListView, Static

from deepagents_cli.config import settings
from deepagents_cli.skills.load import list_skills
from deepagents_cli.widgets.skills_messages import SkillsCancelled, SkillsSelected

if TYPE_CHECKING:
    from textual.app import ComposeResult


class SkillsModal(ModalScreen[dict[str, str] | None]):
    """Modal screen for browsing and selecting skills.

    Displays skills in a simple list view with keyboard navigation.
    Returns the selected skill name and description, or None if cancelled.
    """

    BINDINGS = [
        Binding("enter", "select", "Select skill", show=False),
        Binding("escape", "cancel", "Cancel", show=False),
    ]

    DEFAULT_CSS = """
    SkillsModal {
        align: center middle;
    }

    SkillsModal > Vertical {
        width: 80%;
        height: 70%;
        max-width: 100;
        max-height: 30;
        border: solid $primary;
        background: $surface;
        padding: 1 2;
    }

    SkillsModal .header {
        height: auto;
        padding: 1 0;
        margin-bottom: 1;
        text-align: center;
    }

    SkillsModal .title {
        text-style: bold;
        color: $primary;
    }

    SkillsModal .subtitle {
        color: $text-muted;
        margin-top: 1;
    }

    SkillsModal ListView {
        width: 100%;
        height: 1fr;
        border: solid $primary-darken-2;
        background: $surface-darken-1;
    }

    SkillsModal ListItem {
        padding: 1;
        height: auto;
    }

    SkillsModal ListItem:hover {
        background: $primary-darken-2;
    }

    SkillsModal ListItem.--highlight {
        background: $primary;
        color: $text;
    }

    SkillsModal .skill-item-content {
        width: 100%;
        height: auto;
    }

    SkillsModal .skill-name {
        text-style: bold;
        color: $text;
    }

    SkillsModal .skill-desc {
        color: $text-muted;
        text-style: dim;
        margin-top: 1;
    }

    SkillsModal .skill-source {
        color: $text-muted;
        text-style: italic;
    }

    SkillsModal .footer {
        height: auto;
        padding: 1 0;
        margin-top: 1;
        text-align: center;
        color: $text-muted;
        text-style: dim;
    }

    SkillsModal .empty-state {
        height: 1fr;
        content-align: center middle;
        color: $text-muted;
        text-style: italic;
    }
    """

    def __init__(
        self,
        agent: str = "agent",
        project_skills_dir: Path | None = None,
        **kwargs,
    ) -> None:
        """Initialize SkillsModal.

        Args:
            agent: The agent identifier to show skills for.
            project_skills_dir: Optional path to project skills directory.
            **kwargs: Additional arguments passed to ModalScreen.
        """
        super().__init__(**kwargs)
        self._agent = agent
        self._project_skills_dir = project_skills_dir
        self._skills: list = []
        self._list_view: ListView | None = None

    def compose(self) -> ComposeResult:
        """Compose the modal layout."""
        with Vertical():
            # Header
            with Static(classes="header"):
                yield Label("Available Skills", classes="title")
                yield Label(f"Agent: {self._agent}", classes="subtitle")

            # List view for skills
            self._list_view = ListView(classes="skills-list")
            yield self._list_view

            # Empty state message (hidden by default)
            empty_msg = Static("No skills available", classes="empty-state")
            empty_msg.display = False
            yield empty_msg

            # Footer with navigation hints
            yield Static(
                "↑↓ Navigate | Enter Select | Esc Cancel",
                classes="footer",
            )

    def on_mount(self) -> None:
        """Load skills when the modal is mounted."""
        self._load_skills()
        if self._list_view:
            self._list_view.focus()

    def _load_skills(self) -> None:
        """Load skills from user and project directories."""
        # Get user skills directory
        user_skills_dir = settings.get_user_skills_dir(self._agent)

        # Load skills from both sources
        self._skills = list_skills(
            user_skills_dir=user_skills_dir,
            project_skills_dir=self._project_skills_dir,
        )

        if not self._skills:
            # Show empty state
            if self._list_view:
                self._list_view.display = False
            empty_msg = self.query_one(".empty-state", Static)
            if empty_msg:
                empty_msg.display = True
            return

        # Create list items for each skill
        if self._list_view:
            for skill in self._skills:
                name = skill.get("name", "Unknown")
                desc = skill.get("description", "No description")
                source = skill.get("source", "user")
                source_label = "[User]" if source == "user" else "[Project]"

                # Create a simple list item with skill info
                from textual.containers import Vertical
                item_content = Vertical(
                    Static(f"{name} {source_label}", classes="skill-name"),
                    Static(desc, classes="skill-desc"),
                    classes="skill-item-content",
                )
                item = ListItem(item_content, id=f"skill-{name}")
                self._list_view.append(item)

    def action_select(self) -> None:
        """Select the currently highlighted skill."""
        if not self._list_view or not self._skills:
            return

        selected_index = self._list_view.index
        if selected_index is None or selected_index < 0 or selected_index >= len(self._skills):
            return

        skill = self._skills[selected_index]
        skill_name = skill.get("name", "")
        skill_description = skill.get("description", "")

        self.post_message(SkillsSelected(skill_name))
        self.dismiss({"name": skill_name, "description": skill_description})

    def action_cancel(self) -> None:
        """Cancel the modal and close without selection."""
        self.post_message(SkillsCancelled())
        self.dismiss(None)

    def on_list_view_selected(self, event) -> None:
        """Handle list view selection (Enter key or click)."""
        self.action_select()
