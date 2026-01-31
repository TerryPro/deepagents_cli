"""Title generator for conversation threads."""

from langchain_core.language_models import BaseChatModel

from deepagents_cli.config import create_model


class TitleGenerator:
    """Generate concise titles for conversation threads."""

    def __init__(self, model: BaseChatModel | None = None) -> None:
        """Initialize with optional model.

        Args:
            model: LLM model to use. If None, uses default from config.
        """
        self.model = model or self._create_default_model()

    def _create_default_model(self) -> BaseChatModel:
        """Create default lightweight model for title generation."""
        # Use the same model creation logic but with low-cost settings
        model = create_model(None)
        # Configure for low-cost generation
        if hasattr(model, "temperature"):
            model.temperature = 0.3  # type: ignore
        if hasattr(model, "max_tokens"):
            model.max_tokens = 20  # type: ignore
        return model

    async def generate_title(self, first_message: str) -> str | None:
        """Generate title from first user message.

        Args:
            first_message: User's first message in the conversation

        Returns:
            Generated title or None if generation fails
        """
        try:
            # Truncate long messages
            content = first_message[:200] if len(first_message) > 200 else first_message

            prompt = f"""Generate a concise title (2-4 Chinese words or 3-5 English words) for this conversation.
Return ONLY the title, nothing else.

User message: {content}

Title:"""

            response = await self.model.ainvoke(prompt)
            title = self._clean_title(str(response.content))

            # Validate length
            if len(title) > 30:
                title = title[:27] + "..."

            return title if title else None

        except Exception:
            # Silent failure - don't affect user experience
            return None

    def _clean_title(self, raw: str) -> str:
        """Clean generated title."""
        return raw.strip().strip('"\'').strip()
