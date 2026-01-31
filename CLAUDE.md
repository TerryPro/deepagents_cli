# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build and Development Commands

This project uses `uv` for package management and `make` for task automation.

### Testing
- `make test` - Run unit tests (with socket disable on non-Windows)
- `make test TEST_FILE=<path>` - Run specific test file
- `make integration_test` - Run integration tests (requires `ANTHROPIC_API_KEY`)
- `make test_watch` - Run tests in watch mode
- `make benchmark` - Run benchmark tests
- `make coverage` - Run tests with coverage report

### Linting and Formatting
- `make lint` - Run Ruff linter
- `make format` - Format code with Ruff
- `make check_imports` - Check imports using custom script

### Running
- `make run` - Run CLI using `uvx --no-cache --reinstall .`
- `uv run deepagents` - Run in development mode

## Architecture Overview

### Entry Points
- `deepagents_cli/main.py:cli_main()` - Main CLI entry point
- `deepagents_cli/__init__.py` - Package entry, exports `cli_main`
- Console scripts: `deepagents` and `deepagents-cli` both map to `deepagents_cli:cli_main`

### Core Components

**Agent Creation** (`deepagents_cli/agent.py`):
- `create_cli_agent()` - Factory function that creates a configured DeepAgent
- Supports both local mode (FilesystemBackend + ShellMiddleware) and remote sandbox mode
- Middleware stack: MemoryMiddleware → SkillsMiddleware → LocalContextMiddleware/ShellMiddleware
- Human-in-the-loop via `interrupt_on` config for destructive tools (shell, write_file, edit_file, web_search, fetch_url, task)

**Configuration** (`deepagents_cli/config.py`):
- `settings` - Global settings singleton with user directories, API keys, model config
- `create_model()` - Creates LLM model based on available API keys (OpenAI → Anthropic → Google priority)
- User data stored in `~/.deepagents/` (agent memory, skills, sessions)

**TUI Application** (`deepagents_cli/app.py`):
- Textual-based terminal UI
- Manages conversation state, token tracking, streaming responses

**Session Management** (`deepagents_cli/sessions.py`):
- SQLite-backed checkpointing for conversation persistence
- Thread resume support (`-r` flag)

### Sandboxing
Remote sandbox support via `deepagents_cli/integrations/`:
- `sandbox_factory.py` - Factory for creating sandbox backends
- `modal_integration.py` - Modal sandbox support
- `daytona.py` - Daytona sandbox support
- `runloop.py` - Runloop sandbox support

In sandbox mode, file operations and code execution happen remotely. In local mode, ShellMiddleware provides local shell access.

### Skills System
Skills are reusable workflows stored in:
- User skills: `~/.deepagents/{agent}/skills/`
- Project skills: `.deepagents/skills/` (in project root)

Skills are loaded via `SkillsMiddleware` and invoked through the `skill` tool.

### Code Quality
- **Ruff** for linting and formatting (line length: 100)
- **Google-style** docstrings
- All rules enabled by default with specific ignores per file in `pyproject.toml`
- Tests use `pytest` with asyncio support, timeout (10s default), and socket disable

### Testing Requirements
- Unit tests: No API keys required
- Integration tests: Requires `ANTHROPIC_API_KEY`
- Optional: `LANGSMITH_API_KEY` for tracing
