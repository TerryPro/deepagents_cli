# AGENTS.md - DeepAgents CLI Development Guide

This file provides guidance for agentic coding agents working in this repository.

## Build & Development Commands

This project uses `uv` for package management and `make` for task automation.

### Testing
- `make test` - Run unit tests (socket disabled on non-Windows)
- `make test TEST_FILE=tests/unit_tests/test_config.py` - Run single test file
- `make integration_test` - Run integration tests (requires `ANTHROPIC_API_KEY`)
- `make test_watch` - Run tests in watch mode
- `make benchmark` - Run benchmark tests
- `make coverage` - Run tests with coverage report

### Linting and Formatting
- `make lint` - Run Ruff linter
- `make format` - Format code with Ruff (auto-fix issues)
- `make check_imports` - Check imports using custom script
- `make lint_package` - Lint only the package
- `make lint_tests` - Lint only tests

### Running
- `make run` - Run CLI using `uvx --no-cache --reinstall .`
- `uv run deepagents` - Run in development mode

## Code Style Guidelines

### General
- **Line length**: 100 characters (configured in pyproject.toml)
- **Ruff**: All rules enabled by default with specific per-file ignores
- **Formatter**: Ruff with `docstring-code-format = true`

### Imports
- Use `combine-as-imports = true` (combine multiple imports from same module)
- First-party imports: `deepagents_cli` is known-first-party
- Import order: stdlib → third-party → first-party
- Avoid star imports (`from module import *`)

### Docstrings
- **Google-style** docstrings required
- Use triple double quotes (`"""`)
- Module-level docstrings should describe the file purpose
- Function docstrings should describe args and returns

### Type Hints
- Use type hints for function parameters and return types
- Use `from __future__ import annotations` for forward references (Python 3.11+)
- Use specific types rather than `Any` where possible

### Naming Conventions
- **Functions/variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private functions**: `_leading_underscore`

### Error Handling
- Prefer specific exception types over bare `except:`
- Use `try/except` blocks with meaningful error messages
- Use Rich console for user-facing error messages
- Log errors appropriately for debugging

### Testing Patterns
- Tests located in `tests/unit_tests/` and `tests/integration_tests/`
- Use pytest with fixture-based setup
- Use test classes for grouping related tests
- Mock external dependencies with `unittest.mock`
- Default timeout: 10 seconds (configured in pyproject.toml)

### Code Organization
- **Package**: `deepagents_cli/` - Main CLI implementation
- **Core**: `deepagents_cli/core/` - Core API, sessions, environment
- **Integrations**: `deepagents_cli/integrations/` - Sandbox providers (Modal, Daytona, Runloop)
- **Textual UI**: `deepagents_cli/textual_app/` - TUI components
- **Widgets**: `deepagents_cli/widgets/` - Reusable UI components
- **Skills**: `deepagents_cli/skills/` - Skill system implementation

### Key Dependencies
- `deepagents` - Core agent framework
- `langchain` / `langgraph` - LLM orchestration
- `textual` - Terminal UI framework
- `rich` - Rich text and beautiful formatting
- `uv` - Package manager

### Environment Variables
- `OPENAI_API_KEY` - OpenAI models (priority 1)
- `ANTHROPIC_API_KEY` - Anthropic models (priority 2)
- `GOOGLE_API_KEY` - Google models (priority 3)
- `LANGSMITH_API_KEY` - Optional tracing
- `DEEPAGENTS_LANGSMITH_PROJECT` - Override LangSmith project
