# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Claude Agent SDK sample project demonstrating various agent implementations using the Anthropic Claude Agent SDK.

## Commands

```bash
uv sync              # Install dependencies
uv run <agent>.py    # Run an agent
```

## Entry Points

| File | Description |
|------|-------------|
| `bug_finder.py` | Code review and bug detection agent |
| `claude_sample.py` | Basic Claude API integration |
| `custom_tools.py` | Custom MCP tools (weather, calculator, currency) |
| `hooks_sample.py` | Pre/Post tool hooks for security and logging |
| `web_researcher.py` | Web search and report generation with Brave Search |

## Architecture

- **Single project**: Uses `pyproject.toml` for dependency management (uv)
- **Entry points**: Each `*-agent.py` file is a standalone executable
- **Shared utilities**: `utils/` package contains reusable components:
  - `utils/env.py`: Environment loading (`.env` file)
  - `utils/display.py`: Agent message formatting and display
  - `utils/hooks.py`: Hook factories (bash validation, tool logging)

## Configuration

1. Copy `.env.example` to `.env`
2. Set required API keys:
   - `ANTHROPIC_API_KEY` - Required for all agents
   - `BRAVE_API_KEY` - Required for `web_researcher.py`

## Model Configuration

Default model is `qwen3.5-plus` via Alibaba Cloud DashScope. Configure in `.env`:
```
ANTHROPIC_BASE_URL=https://coding-intl.dashscope.aliyuncs.com/apps/anthropic
ANTHROPIC_MODEL=qwen3.5-plus
```
