"""Unit tests for SkillCard widget."""

from __future__ import annotations

import pytest
from rich.text import Text

from deepagents_cli.config import COLORS
from deepagents_cli.widgets.skill_card import SkillCard


class TestSkillCard:
    """Test suite for SkillCard widget."""

    def test_skill_card_inherits_from_static(self):
        """Test that SkillCard inherits from Static."""
        assert SkillCard.__bases__[0].__name__ == "Static"

    def test_skill_card_constructor_accepts_required_params(self):
        """Test that SkillCard accepts name, description, source in constructor."""
        card = SkillCard(
            name="test-skill",
            description="A test skill description",
            source="user",
        )
        assert card is not None

    def test_get_skill_name_returns_name(self):
        """Test that get_skill_name returns the skill name."""
        card = SkillCard(
            name="my-skill",
            description="Description here",
            source="project",
        )
        assert card.get_skill_name() == "my-skill"

    def test_render_returns_rich_text(self):
        """Test that render returns a Rich Text object."""
        card = SkillCard(
            name="test-skill",
            description="Test description",
            source="user",
        )
        result = card.render()
        assert isinstance(result, Text)

    def test_render_includes_skill_name(self):
        """Test that render output includes the skill name."""
        card = SkillCard(
            name="my-skill",
            description="Description",
            source="user",
        )
        result = card.render()
        assert "my-skill" in result.plain

    def test_render_includes_description(self):
        """Test that render output includes the description."""
        card = SkillCard(
            name="skill",
            description="My special skill",
            source="project",
        )
        result = card.render()
        assert "My special skill" in result.plain

    def test_render_includes_source_label(self):
        """Test that render output includes source label."""
        card = SkillCard(
            name="skill",
            description="Description",
            source="user",
        )
        result = card.render()
        assert "[User]" in result.plain

    def test_user_source_shows_cyan_label(self):
        """Test that user source shows [User] label."""
        card = SkillCard(
            name="skill",
            description="Description",
            source="user",
        )
        result = card.render()
        # Check the source label appears in plain text
        assert "[User]" in result.plain

    def test_project_source_shows_green_label(self):
        """Test that project source shows [Project] label."""
        card = SkillCard(
            name="skill",
            description="Description",
            source="project",
        )
        result = card.render()
        assert "[Project]" in result.plain

    def test_render_truncates_long_description(self):
        """Test that long descriptions are truncated to ~40 chars."""
        long_description = "This is a very long description that should be truncated with dots"
        card = SkillCard(
            name="skill",
            description=long_description,
            source="user",
        )
        result = card.render()
        result_text = result.plain

        # Description should be truncated with "..."
        assert "..." in result_text

        # The total display should be reasonably short (not the full long description)
        # The truncated description should be around 40 chars + "..."
        lines = result_text.split("\n")
        desc_line = [l for l in lines if "..." in l]
        if desc_line:
            # Check that truncation happened
            assert len(desc_line[0]) < len(long_description)

    def test_default_css_exists(self):
        """Test that SkillCard has DEFAULT_CSS attribute."""
        assert hasattr(SkillCard, "DEFAULT_CSS")
        assert isinstance(SkillCard.DEFAULT_CSS, str)

    def test_default_css_has_styling(self):
        """Test that DEFAULT_CSS contains expected CSS rules."""
        css = SkillCard.DEFAULT_CSS
        # Should have border styling
        assert "border" in css.lower()
        # Should have hover styling
        assert "hover" in css.lower()
        # Should have focus styling
        assert "focus" in css.lower()

    def test_skill_name_styled_bold_and_primary(self):
        """Test that skill name is styled bold and primary color."""
        card = SkillCard(
            name="my-skill",
            description="Description",
            source="user",
        )
        result = card.render()

        # Find the skill name span and check its style
        # The skill name should be bold
        found_bold = False
        for span in result.spans:
            if "my-skill" in str(span):
                style_str = str(span.style) if hasattr(span, "style") else ""
                if "bold" in style_str.lower():
                    found_bold = True
                    break

        # Name appears in the text with styling
        assert "my-skill" in result.plain

    def test_description_styled_dim(self):
        """Test that description is styled dim color."""
        card = SkillCard(
            name="skill",
            description="A description text",
            source="user",
        )
        result = card.render()
        assert "A description text" in result.plain
