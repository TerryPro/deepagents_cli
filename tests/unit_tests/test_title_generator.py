"""Tests for title generator."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from deepagents_cli.title_generator import TitleGenerator


class TestTitleGenerator:
    """Test TitleGenerator functionality."""

    def test_clean_title_removes_quotes(self):
        """Test that quotes are stripped from titles."""
        # Mock the model to avoid API calls
        mock_model = MagicMock()
        generator = TitleGenerator(model=mock_model)
        assert generator._clean_title('"Hello World"') == "Hello World"
        assert generator._clean_title("'Hello World'") == "Hello World"
        assert generator._clean_title("  Hello World  ") == "Hello World"

    def test_clean_title_empty(self):
        """Test cleaning empty/whitespace strings."""
        mock_model = MagicMock()
        generator = TitleGenerator(model=mock_model)
        assert generator._clean_title("  ") == ""
        assert generator._clean_title('"  "') == ""


class TestTitleGeneratorAsync:
    """Async tests for title generation."""

    @pytest.mark.asyncio
    async def test_generate_title_with_mock_model(self):
        """Test title generation with mocked model."""
        mock_model = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = "Test Title"
        mock_model.ainvoke.return_value = mock_response

        generator = TitleGenerator(model=mock_model)
        result = await generator.generate_title("Hello, this is a test message")

        assert result == "Test Title"
        mock_model.ainvoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_title_cleans_quotes(self):
        """Test that generated titles are cleaned of quotes."""
        mock_model = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = '"Quoted Title"'
        mock_model.ainvoke.return_value = mock_response

        generator = TitleGenerator(model=mock_model)
        result = await generator.generate_title("Test message")

        assert result == "Quoted Title"

    @pytest.mark.asyncio
    async def test_generate_title_truncates_long_titles(self):
        """Test that very long titles are truncated."""
        mock_model = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = "A" * 50
        mock_model.ainvoke.return_value = mock_response

        generator = TitleGenerator(model=mock_model)
        result = await generator.generate_title("Test")

        assert result == "A" * 27 + "..."
        assert len(result) == 30

    @pytest.mark.asyncio
    async def test_generate_title_handles_empty_response(self):
        """Test that empty response returns None."""
        mock_model = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = "   "
        mock_model.ainvoke.return_value = mock_response

        generator = TitleGenerator(model=mock_model)
        result = await generator.generate_title("Test")

        assert result is None

    @pytest.mark.asyncio
    async def test_generate_title_handles_exception(self):
        """Test that exceptions return None."""
        mock_model = AsyncMock()
        mock_model.ainvoke.side_effect = Exception("API Error")

        generator = TitleGenerator(model=mock_model)
        result = await generator.generate_title("Test")

        assert result is None

    @pytest.mark.asyncio
    async def test_generate_title_truncates_long_messages(self):
        """Test that long messages are truncated before sending to model."""
        mock_model = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = "Short Title"
        mock_model.ainvoke.return_value = mock_response

        generator = TitleGenerator(model=mock_model)
        long_message = "A" * 1000
        await generator.generate_title(long_message)

        # Check that the invoke was called with truncated content
        call_args = mock_model.ainvoke.call_args[0][0]
        assert len(call_args) < 500  # Should be much shorter than 1000 chars
