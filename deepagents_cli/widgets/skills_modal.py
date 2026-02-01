"""SkillsModal screen for browsing and selecting skills.

This module provides a modal screen for displaying all available skills
in a grid layout with keyboard and mouse navigation.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.containers import Grid, Vertical
from textual.screen import ModalScreen
from textual.widgets import Label, Static

from deepagents_cli.config import COLORS, settings
from deepagents_cli.skills.load import list_skills
from deepagents_cli.widgets.skill_card import SkillCard
from deepagents_cli.widgets.skills_messages import SkillsCancelled, SkillsSelected

if TYPE_CHECKING:
    from textual.app import ComposeResult


class SkillsModal(ModalScreen[str | None]):
    """Modal screen for browsing and selecting skills.

    Displays skills in a grid layout with keyboard navigation (arrow keys)
    and mouse click support. Returns the selected skill name or None if cancelled.

    Attributes:
        BINDINGS: Key bindings for navigation and selection.
        DEFAULT_CSS: Textual CSS styling for the modal.
    """

    BINDINGS = [
        Binding("up", "navigate_up", "Navigate up", show=False),
        Binding("down", "navigate_down", "Navigate down", show=False),
        Binding("left", "navigate_left", "Navigate left", show=False),
        Binding("right", "navigate_right", "Navigate right", show=False),
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
        border: solid $primary;
        background: $surface;
        padding: 1;
    }

    SkillsModal .header {
        height: auto;
        padding: 1 0;
        margin-bottom: 1;
    }

    SkillsModal .title {
        text-align: center;
        text-style: bold;
        color: $primary;
    }

    SkillsModal .subtitle {
        text-align: center;
        color: $text-muted;
        margin-top: 1;
    }

    SkillsModal .grid {
        grid-size: 2;
        grid-columns: 1fr 1fr;
        grid-rows: auto;
        height: 1fr;
        overflow-y: auto;
    }

    SkillsModal .footer {
        height: auto;
        padding: 1 0;
        margin-top: 1;
        text-align: center;
        color: $text-muted;
    }

    SkillsModal .empty-state {
        height: 1fr;
        content-align: center middle;
        color: $text-muted;
        text-style: italic;
    }

    SkillsModal SkillCard {
        border: solid $primary-darken-2;
        background: $surface;
        padding: 1;
    }

    SkillsModal SkillCard.selected {
        border: solid $primary;
        background: $primary-darken-1;
    }

    SkillsModal SkillCard:focus {
        border: double $primary;
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
        self._skill_cards: list[SkillCard] = []
        self._selected_index = -1
        self._grid: Grid | None = None
        self._empty_message: Static | None = None

    def compose(self) -> ComposeResult:
        """Compose the modal layout.

        Yields:
            UI components for the modal.
        """
        with Vertical():
            # Header
            with Static(classes="header"):
                yield Label("Available Skills", classes="title")
                yield Label(f"Agent: {self._agent}", classes="subtitle")

            # Grid container for skills
            self._grid = Grid(classes="grid")
            yield self._grid

            # Empty state message (hidden by default)
            self._empty_message = Static("No skills available", classes="empty-state")
            self._empty_message.display = False
            yield self._empty_message

            # Footer with navigation hints
            yield Static(
                "↑↓←→ Navigate | Enter Select | Esc Cancel | Click to select",
                classes="footer",
            )

    def on_mount(self) -> None:
        """Load skills when the modal is mounted."""
        self._load_skills()

    def _load_skills(self) -> None:
        """Load skills from user and project directories.

        Fetches skills using list_skills() and creates SkillCard widgets
        for each skill. Handles empty state by showing a message.
        """
        # Get user skills directory
        user_skills_dir = settings.get_user_skills_dir(self._agent)

        # Load skills from both sources
        skills = list_skills(
            user_skills_dir=user_skills_dir,
            project_skills_dir=self._project_skills_dir,
        )

        if not skills:
            # Show empty state
            if self._grid:
                self._grid.display = False
            if self._empty_message:
                self._empty_message.display = True
            return

        # Create skill cards
        if self._grid:
            self._grid.remove_children()
            self._skill_cards = []

            for skill in skills:
                card = SkillCard(
                    name=skill["name"],
                    description=skill.get("description", ""),
                    source=skill.get("source", "user"),
                )
                self._skill_cards.append(card)
                self._grid.mount(card)

            # Select first skill if available
            if self._skill_cards:
                self._selected_index = 0
                self._update_selection()

    def _update_selection(self) -> None:
        """Update the visual selection state of skill cards.

        Sets focus on the currently selected card and removes focus from others.
        """
        if not self._skill_cards:
            return

        for i, card in enumerate(self._skill_cards):
            if i == self._selected_index:
                card.add_class("selected")
            else:
                card.remove_class("selected")

        # Focus the selected card for visual feedback
        if 0 <= self._selected_index < len(self._skill_cards):
            self._skill_cards[self._selected_index].focus()

    def action_navigate_up(self) -> None:
        """Navigate up in the skill grid (move to previous row)."""
        if not self._skill_cards or self._selected_index < 0:
            return

        # In a 2-column grid, move up 2 positions
        new_index = self._selected_index - 2
        if new_index < 0:
            # Wrap around to bottom
            new_index = len(self._skill_cards) - 1

        self._selected_index = new_index
        self._update_selection()

    def action_navigate_down(self) -> None:
        """Navigate down in the skill grid (move to next row)."""
        if not self._skill_cards:
            return

        # In a 2-column grid, move down 2 positions
        new_index = self._selected_index + 2
        if new_index >= len(self._skill_cards):
            # Wrap around to top
            new_index = 0

        self._selected_index = new_index
        self._update_selection()

    def action_navigate_left(self) -> None:
        """Navigate left in the skill grid."""
        if not self._skill_cards or self._selected_index < 0:
            return

        # Move left 1 position
        new_index = self._selected_index - 1
        if new_index < 0:
            # Wrap around to end
            new_index = len(self._skill_cards) - 1

        self._selected_index = new_index
        self._update_selection()

    def action_navigate_right(self) -> None:
        """Navigate right in the skill grid."""
        if not self._skill_cards:
            return

        # Move right 1 position
        new_index = self._selected_index + 1
        if new_index >= len(self._skill_cards):
            # Wrap around to start
            new_index = 0

        self._selected_index = new_index
        self._update_selection()

    def action_select(self) -> None:
        """Select the currently highlighted skill.

        Posts a SkillsSelected message with the skill name and dismisses the modal.
        """
        if not self._skill_cards or self._selected_index < 0:
            return

        selected_skill = self._skill_cards[self._selected_index]
        skill_name = selected_skill.get_skill_name()

        self.post_message(SkillsSelected(skill_name))
        self.dismiss(skill_name)

    def action_cancel(self) -> None:
        """Cancel the modal and close without selection.

        Posts a SkillsCancelled message and dismisses with None.
        """
        self.post_message(SkillsCancelled())
        self.dismiss(None)

    def on_click(self, event) -> None:
        """Handle click events on skill cards.

        Args:
            event: The click event from Textual.
        """
        # Check if a skill card was clicked
        clicked_widget = event.widget
        for i, card in enumerate(self._skill_cards):
            if card == clicked_widget:
                self._selected_index = i
                self._update_selection()
                self.action_select()
                break
