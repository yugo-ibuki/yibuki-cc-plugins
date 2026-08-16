# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Claude Code plugin collection repository (`yibuki-cc-plugins`). Provides custom slash commands and skills that extend Claude Code's capabilities through the `.claude-plugin` system.

## Architecture

```
.claude-plugin/marketplace.json    # Plugin registry
plugins/                           # Individual plugin directories
```

## Command Definition Format

Commands (`commands/*.md`) use YAML frontmatter:

```yaml
---
allowed-tools:          # Tools the command can use
  - Bash(git:*)
  - Read
  - Write
description:            # Brief description (shown in command list)
argument-hint:          # Placeholder for arguments
model:                  # Optional: specific model
---
```

## Skill Definition Format

Skills (`skills/*.md`) use YAML frontmatter with official fields only:

```yaml
---
name: skill-name                    # Required: lowercase, hyphens, max 64 chars
description: What it does and when  # Required: max 1024 chars, include triggers
version: "1.0.0"                    # Optional
model: claude-sonnet-4-20250514              # Optional
allowed-tools:                      # Optional: limit available tools
  - Read
  - Glob
disable-model-invocation: false     # Optional: prevent auto-invocation
---
```

## Adding New Plugins

1. Create `plugins/<plugin-name>/`
2. Add `plugins/<plugin-name>/.claude-plugin/plugin.json`
3. Add commands in `commands/` and/or skills in `skills/`
4. Register in `.claude-plugin/marketplace.json`

## Key Patterns

- All user-facing text in Japanese (日本語)
