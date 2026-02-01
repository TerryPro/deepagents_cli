"""SkillCard widget for displaying skills in the skills modal."""

from __future__ import annotations

from rich.text import Text
from textual.widgets import Static

from deepagents_cli.config import COLORS


class SkillCard(Static):
    """Widget displaying a single skill with name, description, and source.

    Attributes:
        DEFAULT_CSS: Textual CSS styling for border, hover, and focus states.
    """

    DEFAULT_CSS = """
    SkillCard {
        height: auto;
        padding: 1;
        border: solid $primary;
        margin: 1;
    }

    SkillCard:hover {
        border: solid $accent;
        background: $surface-darken-1;
    }

    SkillCard:focus {
        border: double $accent;
        background: $surface-darken-1;
    }
    """

    def __init__(self, name: str, description: str, source: str, **kwargs) -> None:
        """Initialize SkillCard with skill details.

        Args:
            name: The skill name to display.
            description: The skill description to display.
            source: The source label ('user' or 'project').
            **kwargs: Additional arguments passed to Static.
        """
        super().__init__(**kwargs)
        self._name = name
        self._description = description
        self._source = source.lower()

    def get_skill_name(self) -> str:
        """Return the skill name.

        Returns:
            The skill name string.
        """
        return self._name

    def _get_source_label(self) -> str:
        """Get the formatted source label.

        Returns:
            Formatted source label string.
        """
        if self._source == "user":
            return "[User]"
        elif self._source == "project":
            return "[Project]"
        return f"[{self._source}]"

    def _truncate_description(self, text: str, max_length: int = 40) -> str:
        """Truncate description to max length with ellipsis.

        Args:
            text: Description text to truncate.
            max_length: Maximum length before truncation.

        Returns:
            Truncated text with "..." if needed.
        """
        if len(text) <= max_length:
            return text
        return text[: max_length - 3] + "..."

    def render(self) -> Text:
        """Render the skill card as Rich text.

        Returns:
            Rich Text object with formatted skill info.
        """
        # Build the skill card text
        card = Text()

        # Skill name (bold, primary color)
        card.append(self._name, style=f"bold {COLORS['primary']}")
        card.append(" ")

        # Source label
        source_label = self._get_source_label()
        if self._source == "user":
            card.append(source_label, style="cyan")
        elif self._source == "project":
            card.append(source_label, style="green")
        else:
            card.append(source_label, style="dim")

        card.append("\n")

        # Description (dim color, truncated)
        truncated_desc = self._truncate_description(self._description)
        card.append(truncated_desc, style=COLORS["dim"])

        return card
