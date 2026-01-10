# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Claude Code plugin collection repository (`yibuki-cc-plugins`). Provides custom slash commands and skills that extend Claude Code's capabilities through the `.claude-plugin` system.

## Architecture

```
.claude-plugin/marketplace.json    # Plugin registry
plugins/
  ├── pr-creator/                  # Git commit & PR creation
  │   ├── .claude-plugin/plugin.json
  │   ├── commands/pr-creator.md
  │   └── assets/PR_TEMPLATE.md
  └── custom-doc/                  # Documentation management
      ├── .claude-plugin/plugin.json
      ├── commands/                # Slash commands
      │   ├── create-doc.md
      │   ├── update-doc.md
      │   ├── create-investigate-doc.md
      │   └── update-investigate-doc.md
      ├── scripts/
      │   ├── markdown-to-html.py
      │   └── select-doc.py
      └── skills/                  # Internal skills (auto-invoked by commands)
          ├── search-related-docs.md
          ├── load-doc-context.md
          └── doc-to-html.md
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

## Available Commands

| Command | Description |
|---------|-------------|
| `/pr-creator` | Creates git commits and PRs |
| `/create-doc` | Creates documentation in `.claude/custom-documents/` |
| `/update-doc` | Updates existing documentation |
| `/create-investigate-doc` | Creates investigation reports |
| `/update-investigate-doc` | Updates investigation reports |

## Scripts

```bash
# Generate HTML from Markdown
python plugins/custom-doc/scripts/markdown-to-html.py <file_or_directory>

# Interactive document selection
python plugins/custom-doc/scripts/select-doc.py [keyword]
```

## Adding New Plugins

1. Create `plugins/<plugin-name>/`
2. Add `plugins/<plugin-name>/.claude-plugin/plugin.json`
3. Add commands in `commands/` and/or skills in `skills/`
4. Register in `.claude-plugin/marketplace.json`

## Key Patterns

- Documents go to `.claude/custom-documents/<name>/` in target projects
- Commands reference skills via `## 参照スキル` section
- Skills auto-search related docs before create/update operations
- All user-facing text in Japanese (日本語)
