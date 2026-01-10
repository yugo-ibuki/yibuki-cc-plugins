# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Claude Code plugin collection repository (`yibuki-cc-plugins`). It provides custom slash commands that extend Claude Code's capabilities through the `.claude-plugin` system.

## Architecture

```
.claude-plugin/marketplace.json    # Plugin registry - lists all available plugins
plugins/
  ├── pr-creator/                  # Git commit & PR creation plugin
  │   ├── .claude-plugin/plugin.json
  │   ├── commands/pr-creator.md   # Slash command definition
  │   └── assets/PR_TEMPLATE.md
  └── custom-doc/                  # Documentation management plugin
      ├── .claude-plugin/plugin.json
      ├── commands/                # Slash command definitions
      │   ├── create-doc.md        # /create-doc command
      │   ├── create-investigate-doc.md  # /create-investigate-doc command
      │   └── update-doc.md        # /update-doc command
      ├── scripts/                 # Helper scripts
      │   ├── markdown-to-html.py  # MD→HTML converter with TOC
      │   └── select-doc.py        # Interactive document selector
      └── skills/                  # Skill definitions and examples
```

## Plugin Command Structure

Each command is defined as a markdown file with YAML frontmatter:

```yaml
---
allowed-tools:          # Tools the command can use
  - Bash(git:*)
  - Read
  - Write
description:            # Brief description shown in command list
argument-hint:          # Placeholder for arguments
model:                  # Optional: specific model to use
---
```

## Available Commands

| Command | Plugin | Description |
|---------|--------|-------------|
| `/pr-creator` | pr-creator-plugin | Creates git commits and PRs |
| `/create-doc` | custom-doc-plugin | Creates documentation in `.claude/custom-documents/` |
| `/create-investigate-doc` | custom-doc-plugin | Creates investigation reports for codebase analysis |
| `/update-doc` | custom-doc-plugin | Updates existing documentation with new changes |

## Scripts

**Generate HTML from Markdown:**
```bash
python plugins/custom-doc/scripts/markdown-to-html.py <file_or_directory>
```

**Interactive Document Selection:**
```bash
python plugins/custom-doc/scripts/select-doc.py [keyword]
```

## Adding New Plugins

1. Create directory: `plugins/<plugin-name>/`
2. Add plugin.json: `plugins/<plugin-name>/.claude-plugin/plugin.json`
3. Add command files: `plugins/<plugin-name>/commands/<command>.md`
4. Register in `.claude-plugin/marketplace.json`

## Key Patterns

- Documents created by custom-doc go to `.claude/custom-documents/<name>/` in target projects
- All commands in Japanese (日本語)
- PR creation flows: status → diff → add → commit → create PR via `gh`
- Document updates track git changes and only add unrecorded files
